# GenVideoAI
Tool for auto generation video

## Microservices

- [api-gateway](api-gateway): FastAPI entrypoint for job submission.
- [orchestrator](orchestrator): Celery worker that coordinates job processing.
- [scenario-service](scenario-service): ChatGPT service for scenario.
- [image-service](image-service): Stable Diffusion image generation service.
- [tts-service](tts-service): Text-to-speech generation service.
- [ambience-service](ambience-service): Text-to-ambient_sound generation service.
- [video-composer](video-composer): FFmpeg-based video assembly.
- [assets](assets): MinIO S3 storage for intermediate artifacts.
- [db](db): PostgreSQL metadata store.
- [broker](broker): RabbitMQ message broker.
- [cache](cache): Redis cache for tokens and rate limiting.
- [observability](observability): ELK stack for monitoring and logs.

## Pipeline
- `api-gateway` - API
  - gets the `task`
  - sent `task` to `broker`
- `orchestrator` - Pipeline handler
  - Get `task` from the `broker`.
  - divides down into `subtasks` and readiness is monitored. 
  - Starting Pipeline
- `scenario-service`: 
  - ChatGPT generate `scenario` by `task`,
  - divides the `scenario` into `chapters`, 
  - sent `scenario` and `chapters` to `broker`
- `image-service`
  - Read `scenario` and `chapters` from `broker`
  - Stable Diffusion generate `image` for each `chapters` or `subchapters`
  - Send `image` to `assets`
  - Send `image` path to `broker`
- `tts-service`
  - Read `scenario` and `chapters` from `broker`
  - Generate `voiceover` for each `chapters`
  - Send `voiceover` to `assets`
  - Send `voiceover` path to `broker`
- `ambience-service`
  - Read `scenario` and `chapters` from `broker`
  - Generate `ambience sound` for each `chapters`
  - Send `ambience sound` to `assets`
  - Send `ambience sound` path to `broker`
- `video-composer/`
  - Read `image`, `voiceover`, `ambience sound` from `broker` for each `chapter`
  - Generate `video`
  - Send `video` to `assets`
  - Send `video` path to `broker`

## License
GenVideoAI is free for non-commercial use under the **GenVideoAI License v1.0**.
For commercial licensing, please contact: grigorio714@gmail.com
