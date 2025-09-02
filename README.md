# GenVideoAI
Tool for auto generation video

## Microservices

- `api-gateway/`: FastAPI entrypoint for job submission.
- `orchestrator/`: Celery worker that coordinates job processing.
- `scenario-service/`: ChatGPT service for scenario.
- `image-service/`: Stable Diffusion image generation service.
- `tts-service/`: Text-to-speech generation service.
- `video-composer/`: FFmpeg-based video assembly.
- `assets/`: MinIO S3 storage for intermediate artifacts.
- `db/`: PostgreSQL metadata store.
- `broker/`: RabbitMQ message broker.
- `cache/`: Redis cache for tokens and rate limiting.
- `observability/`: ELK stack for monitoring and logs.

## License
GenVideoAI is free for non-commercial use under the **GenVideoAI License v1.0**.
For commercial licensing, please contact: grigorio714@gmail.com
