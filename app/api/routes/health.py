from fastapi import APIRouter, Response, status

router = APIRouter()


@router.get(
    "/health",
    summary="Readiness probe",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def get_health() -> Response:
    return Response(status_code=status.HTTP_204_NO_CONTENT)
