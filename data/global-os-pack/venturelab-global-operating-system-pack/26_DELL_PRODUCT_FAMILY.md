# Dell Product Family

Reuse Dell's evidence/identity kernel. Add modality-specific schemas rather than one
giant universal price table.

## VisionTruth / VLRoute

Capture:
- image formats/limits
- resolution behavior
- image token/billing semantics
- OCR/document/chart capability
- vision benchmarks
- latency
- tool support

Use VL-RouterBench as an initial research benchmark adapter.

## VideoTruth / VideoRoute — understanding

Capture:
- max duration
- frame sampling
- codecs/containers
- temporal reasoning benchmarks
- latency
- per-video/per-second/tokenized-media costs

## VideoGenTruth / VideoGenRoute — generation

Capture:
- seconds generated
- resolution
- FPS
- aspect ratio
- audio
- model/quality tier
- queue latency
- failure/refund semantics
- price per generation/unit

Use video-generation benchmarks only as evidence adapters.

## AudioTruth

ASR/TTS/speech-to-speech:
- per minute/character/token pricing
- realtime latency
- diarization
- voice constraints

## VectorTruth

Embeddings/rerank:
- dimensions
- modality
- batch constraints
- throughput
- benchmark evidence
- $/token/request

## ImageGenTruth

- generation/edit/inpainting
- resolution
- quality tier
- latency
- price per image
