#!/usr/bin/env python3
"""Test script to verify deployer module imports"""
import sys
from pathlib import Path

# Add mango directory to path
mango_dir = Path(__file__).parent
sys.path.insert(0, str(mango_dir))

print("Testing deployer module import...")

try:
    from deployer import DeploymentEngine, DeploymentLogger
    print("✅ Successfully imported DeploymentEngine and DeploymentLogger")

    from deployer.modules import (
        GitCloner,
        AIAnalyzer,
        DockerBuilder,
        ECRPusher,
        TerraformRunner,
        CodeDeployManager,
        HealthChecker
    )
    print("✅ Successfully imported all deployer modules")

    from deployer.engine import deploy
    print("✅ Successfully imported deploy function")

    print("\n🎉 All imports successful!")
    print(f"DeploymentEngine: {DeploymentEngine}")
    print(f"deploy function: {deploy}")

except ImportError as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
