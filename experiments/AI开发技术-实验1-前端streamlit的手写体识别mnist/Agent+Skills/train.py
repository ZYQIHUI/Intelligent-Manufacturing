#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MNIST CNN 训练入口
用法: python train.py [--epochs 10] [--batch-size 64] [--lr 0.001]
"""
import argparse
import torch
import torch.optim as optim
from mnist.data import load_data
from mnist.model import MNISTCNN
from mnist.train import train_one_epoch
from mnist.evaluate import evaluate


def main():
    parser = argparse.ArgumentParser(description="MNIST CNN 训练")
    parser.add_argument("--epochs", type=int, default=10, help="训练轮数")
    parser.add_argument("--batch-size", type=int, default=64, help="批次大小")
    parser.add_argument("--lr", type=float, default=0.001, help="学习率")
    parser.add_argument("--device", type=str,
                        default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()

    print(f"设备: {args.device}")
    print(f"训练轮数: {args.epochs}, 批次大小: {args.batch_size}, 学习率: {args.lr}")

    # 加载数据
    print("加载 MNIST 数据...")
    train_loader, test_loader = load_data(batch_size=args.batch_size)

    # 创建模型
    model = MNISTCNN()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    print(f"模型参数量: {sum(p.numel() for p in model.parameters()):,}")

    # 训练
    print("\n开始训练...")
    for epoch in range(1, args.epochs + 1):
        loss = train_one_epoch(model, train_loader, optimizer, device=args.device)
        acc = evaluate(model, test_loader, device=args.device)
        print(f"Epoch {epoch:2d}/{args.epochs} — Loss: {loss:.4f} — Test Acc: {acc:.2f}%")

    # 最终评估
    final_acc = evaluate(model, test_loader, device=args.device)
    print(f"\n最终测试准确率: {final_acc:.2f}%")

    # 保存模型
    torch.save(model.state_dict(), "model.pth")
    print("模型已保存为 model.pth")


if __name__ == "__main__":
    main()
