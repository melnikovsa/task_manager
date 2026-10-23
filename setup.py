from setuptools import setup, find_packages

setup(
    name="task_manager",
    version="0.1.0",
    description="Система управления задачами и комментариями на Django и DRF",
    author="Ваше Имя",
    author_email="your.email@example.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=4.2,<5.0",
        "djangorestframework",
        "djangorestframework-simplejwt",
        "drf-yasg",
        "psycopg2-binary",
    ],
    # Добавляем зависимость для линтинга
    extras_require={
        "dev": [
            "flake8",
        ]
    },
    python_requires=">=3.10",
)
