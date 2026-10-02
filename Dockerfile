FROM python:3.12-slim
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH" TORCH_HOME=/home/user/.cache/torch
ENV DB_PATH=/tmp/predictskin_users.db
ENV KAGGLEHUB_CACHE=/tmp/kagglehub
WORKDIR /home/user/app

# CPU-only PyTorch (much smaller than the default build)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
COPY --chown=user requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Download the pretrained model while building, so starts are fast
RUN python -c "from torchvision import models; models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)"

COPY --chown=user . .
EXPOSE 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
