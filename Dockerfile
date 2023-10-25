FROM python:3.10-slim

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends curl gcc g++ git make && \
    apt-get clean && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* && \
    pip install langflow>=0.5.3 && \
    pip cache purge && \
    rm -rf /root/.cache/pip && \
    useradd -m -u 1000 langflow && \
    mkdir -p /home/langflow/app && \
    chown -R langflow:langflow /home/langflow

USER langflow

ENV HOME=/home/langflow

COPY --chown=langflow:langflow run.sh $HOME/app/run.sh

WORKDIR $HOME/app

ENTRYPOINT ["./run.sh"]

HEALTHCHECK CMD curl --fail http://0.0.0.0:7860/ || exit 1

EXPOSE 7860
