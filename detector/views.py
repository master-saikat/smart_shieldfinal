from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import RegisterSerializer, HistorySerializer
from .nlp_model import predict_scam
from .link_checker import analyze_url
from .genai import generate_explanation, cyber_advice
from .models import ScanHistory


# ─── AUTH ─────────────────────────────────────────────────────────────────────
from django.shortcuts import render

def home(request):
    return render(request, 'xyz.html')

from django.shortcuts import render

def register_page(request):
    return render(request, 'index.html')



@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    """Blacklists the refresh token so it can't be used again."""
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
    except TokenError:
        return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)


# ─── PROFILE ──────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    total_scans = ScanHistory.objects.filter(user=user).count()
    threats     = ScanHistory.objects.filter(user=user, risk_score__gte=60).count()
    safe        = ScanHistory.objects.filter(user=user, risk_score__lt=40).count()

    return Response({
        "username":     user.username,
        "email":        user.email,
        "total_scans":  total_scans,
        "threats_found": threats,
        "safe_results": safe,
    })


# ─── SCAN: TEXT ───────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_text(request):
    message = request.data.get("message", "").strip()
    if not message:
        return Response({"error": "Message is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Input length limit — prevents API abuse and excessive AI costs
    if len(message) > 2000:
        return Response({"error": "Message too long. Max 2000 characters."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        risk_score, label = predict_scam(message)
    except Exception as e:
        return Response({"error": f"ML model error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    ai_available = True
    try:
        ai_explanation = generate_explanation(message, risk_score, label)
    except Exception as e:
        ai_explanation = ""
        ai_available = False

    scan = ScanHistory.objects.create(
        user=request.user,
        scan_type='text',
        input_data=message,
        risk_score=risk_score,
        label=label,
        explanation=ai_explanation,
    )

    return Response({
        "id":           scan.id,
        "risk_score":   risk_score,
        "label":        label,
        "explanation":  ai_explanation,
        "ai_available": ai_available,
    })


# ─── SCAN: LINK ───────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_link(request):
    url = request.data.get("url", "").strip()
    if not url:
        return Response({"error": "URL is required."}, status=status.HTTP_400_BAD_REQUEST)

    if len(url) > 2000:
        return Response({"error": "URL too long. Max 2000 characters."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        risk, label, reasons = analyze_url(url)
    except Exception as e:
        return Response({"error": f"URL analysis error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    explanation = (
        "This link is risky because: " + ", and ".join(reasons) + "."
        if reasons else
        "This link appears safe based on our checks."
    )

    scan = ScanHistory.objects.create(
        user=request.user,
        scan_type='link',
        input_data=url,
        risk_score=risk,
        label=label,
        explanation=explanation,
    )

    return Response({
        "id":          scan.id,
        "risk_score":  risk,
        "label":       label,
        "safe":        label == "Safe",
        "explanation": explanation,
        "reasons":     reasons,
    })


# ─── CYBER CHAT ───────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cyber_chat(request):
    question = request.data.get("question", "").strip()
    if not question:
        return Response({"error": "Question is required."}, status=status.HTTP_400_BAD_REQUEST)

    if len(question) > 1000:
        return Response({"error": "Question too long. Max 1000 characters."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        answer = cyber_advice(question)
    except Exception as e:
        answer = f"AI unavailable: {str(e)}"

    return Response({"answer": answer})


# ─── HISTORY ──────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def history_list(request):
    scans = ScanHistory.objects.filter(user=request.user)   # ordered by Meta
    serializer = HistorySerializer(scans, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def history_detail(request, id):
    try:
        scan = ScanHistory.objects.get(id=id, user=request.user)
    except ScanHistory.DoesNotExist:
        return Response({"error": "Scan not found."}, status=status.HTTP_404_NOT_FOUND)

    return Response(HistorySerializer(scan).data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_history(request, id):
    try:
        scan = ScanHistory.objects.get(id=id, user=request.user)
    except ScanHistory.DoesNotExist:
        return Response({"error": "Scan not found."}, status=status.HTTP_404_NOT_FOUND)

    scan.delete()
    return Response({"message": "Deleted successfully."})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_all_history(request):
    deleted_count, _ = ScanHistory.objects.filter(user=request.user).delete()
    return Response({"message": f"Deleted {deleted_count} records."})