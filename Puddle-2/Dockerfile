FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# Core system dependencies required for PyQt6 and watchdog file watching.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libegl1 \
        libdbus-1-3 \
        libfontconfig1 \
        libfreetype6 \
        libgl1 \
        libglvnd0 \
        libice6 \
        libsm6 \
        libwayland-client0 \
        libx11-xcb1 \
        libxrender1 \
        libxcb1 \
        libxcb-cursor0 \
        libxcb-icccm4 \
        libxcb-image0 \
        libxcb-keysyms1 \
        libxcb-randr0 \
        libxcb-render-util0 \
        libxcb-shm0 \
        libxcb-sync1 \
        libxcb-shape0 \
        libxcb-util1 \
        libxcb-xfixes0 \
        libxcb-xinerama0 \
        libxcb-xkb1 \
        libxcomposite1 \
        libxext6 \
        libxi6 \
        libxkbcommon0 \
        libxkbcommon-x11-0 \
        libxrandr2 \
        libxt6 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libxdamage1 \
        libxcursor1 \
        libgtk-3-0 \
        libgdk-pixbuf-2.0-0 \
        libnss3 \
        libnspr4 \
        libxss1 \
        libxtst6 \
        libgbm1 \
        libdrm2 \
        libxkbfile1 \
        libasound2 \
        libopengl0 \
        libgstreamer1.0-0 \
        libgstreamer-plugins-base1.0-0 \
        gstreamer1.0-plugins-base \
        gstreamer1.0-plugins-good \
        gstreamer1.0-plugins-bad \
        gstreamer1.0-libav \
        gstreamer1.0-alsa \
        gstreamer1.0-pipewire \
        libpipewire-0.3-0 \
        libpipewire-0.3-modules \
        pipewire \
        pulseaudio \
        pulseaudio-utils \
        libpulse0 \
        libkrb5-3 \
        libk5crypto3 \
        libkrb5support0 \
        libgssapi-krb5-2 \
        xauth \
    && rm -rf /var/lib/apt/lists/*

RUN cp /etc/pulse/client.conf /etc/pulse/client-noshm.conf \
    && sed -i "s/;\\s*enable-shm = yes/enable-shm = no/g" /etc/pulse/client-noshm.conf

WORKDIR /workspace

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN mkdir -p /tmp/pipewire-bridge /tmp/pulseaudio-bridge

# Allow Qt to use the host X11 display.
ENV QT_X11_NO_MITSHM=1
ENV QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox"
ENV QTWEBENGINE_DISABLE_SANDBOX=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/workspace/src

CMD ["bash"]
