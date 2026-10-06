FROM mcr.microsoft.com/devcontainers/miniconda:0-3

COPY environment.yml* .devcontainer/noop.txt .devcontainer/conda_init.txt /tmp/conda-tmp/

RUN conda clean --all --yes \
    && if [ -f "/tmp/conda-tmp/environment.yml" ]; then umask 0002 && conda env update --name base --file /tmp/conda-tmp/environment.yml; fi \
    && cat /tmp/conda-tmp/conda_init.txt >> /home/vscode/.bashrc \
    && rm -rf /tmp/conda-tmp
