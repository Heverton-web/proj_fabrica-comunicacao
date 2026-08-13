"""Painel de Controle Universal Multi-Harness da Fábrica de Materiais de Comunicação.

Backend local (FastAPI) que orquestra a Fábrica sem depender de uma sessão
interativa de agente: o usuário escolhe pasta de trabalho, harness/provedor de
LLM e credenciais; o backend dispara o harness escolhido em modo headless.
"""
