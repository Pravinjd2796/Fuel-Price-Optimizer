# Installing Docker for Fuel Price Optimizer

To containerize and run the Fuel Price Optimizer, you need Docker installed on your system.

## macOS Installation

### Option 1: Docker Desktop (Recommended)

1. **Download Docker Desktop:**
   - Visit: https://www.docker.com/products/docker-desktop
   - Download for macOS (Apple Silicon or Intel)

2. **Install:**
   - Open the downloaded `.dmg` file
   - Drag Docker to Applications folder
   - Launch Docker Desktop from Applications

3. **Start Docker Desktop:**
   - Click the Docker icon in the menu bar
   - Wait for Docker to start (whale icon should be steady)

4. **Verify Installation:**
   ```bash
   docker --version
   docker-compose --version
   ```

### Option 2: Using Homebrew

```bash
brew install --cask docker
```

Then launch Docker Desktop from Applications.

## Linux Installation

### Ubuntu/Debian:

```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up the repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add your user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER

# Verify installation
docker --version
```

### CentOS/RHEL:

```bash
# Install required packages
sudo yum install -y yum-utils

# Add Docker repository
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install Docker Engine
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (optional)
sudo usermod -aG docker $USER
```

## Windows Installation

1. **Download Docker Desktop:**
   - Visit: https://www.docker.com/products/docker-desktop
   - Download for Windows

2. **Install:**
   - Run the installer
   - Follow the setup wizard
   - Restart if prompted

3. **Start Docker Desktop:**
   - Launch Docker Desktop from Start Menu
   - Wait for Docker to start

4. **Verify Installation:**
   ```cmd
   docker --version
   docker-compose --version
   ```

## Verify Docker is Working

After installation, test Docker:

```bash
docker run hello-world
```

You should see a success message if Docker is working correctly.

## Next Steps

Once Docker is installed, you can:

1. **Build the Docker image:**
   ```bash
   ./build_docker.sh
   # or
   docker build -t fuel-price-optimizer .
   ```

2. **Run the container:**
   ```bash
   ./run_docker.sh
   # or
   docker-compose up -d
   ```

3. **Test the API:**
   ```bash
   curl http://localhost:8000/health
   ```

## Troubleshooting

### Docker command not found

- **macOS:** Make sure Docker Desktop is running
- **Linux:** Make sure Docker service is running: `sudo systemctl status docker`
- **Windows:** Restart terminal after installation

### Permission denied (Linux)

Add your user to the docker group:
```bash
sudo usermod -aG docker $USER
```
Then log out and log back in.

### Docker Desktop not starting

- Check system requirements
- Ensure virtualization is enabled in BIOS
- Try restarting Docker Desktop

## Resources

- Docker Documentation: https://docs.docker.com/
- Docker Desktop: https://www.docker.com/products/docker-desktop
- Docker Hub: https://hub.docker.com/

