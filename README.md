# GenVideoAI
Tool for auto generation video

## Microservices

- [api-gateway](api-gateway): FastAPI entrypoint for job submission.
- [orchestrator](orchestrator): Celery worker that coordinates job processing.
- [scenario-service](scenario-service): ChatGPT service for scenario.
- [image-service](image-service): Stable Diffusion image generation service.
- [tts-service](tts-service): Text-to-speech generation service.
- [ambient-service](ambient-service.md): Text-to-ambient_sound generation service.
- [render-service](render-service.md): FFmpeg-based video assembly.
- [assets-service](assets-service.md): MinIO S3 storage for intermediate artifacts.
- [db](db): PostgreSQL metadata store.
- [broker](broker): RabbitMQ message broker.
- [cache](cache): Redis cache for tokens and rate limiting.
- [observability](observability): ELK stack for monitoring and logs.

Open with [Obsidian](obsidian://open)

![[Main_Pipeline.canvas]]

Download [Obsidian](https://obsidian.md/) 

## License
GenVideoAI is free for non-commercial use under the **GenVideoAI License v1.0**.
For commercial licensing, please contact: grigorio714@gmail.com
