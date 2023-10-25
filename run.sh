#!/bin/bash

langflow run \
    --workers "$(nproc --all)" \
    --host 0.0.0.0 \
    --port 7860
