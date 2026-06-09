#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模型评估入口
用法: python evaluate.py [--batch-size 64] [--model-path model.pth]
"""
import argparse
import torch
from mnist.data import load_data
from mnist.model import MNISTCNN
from mnist.evaluate import evaluate


def main():
    parser = argparse.ArgumentParser(description="MNIST 模型评估")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--model-path", type=str, default="model.pth")
    parser.add_argument("--device", type=str,
                        default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()

    _, test_loader = load_data(batch_size=args.batch_size)

    model = MNISTCNN()
    model.load_state_dict(
        torch.load(args.model_path, map_location=args.device, weights_only=True)
    )
    print(f"模型已加载: {args.model_path}")

    acc = evaluate(model, test_loader, device=args.device)
    print(f"测试集准确率: {acc:.2f}%")


if __name__ == "__main__":
    main()
