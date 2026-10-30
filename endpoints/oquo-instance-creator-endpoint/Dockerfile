FROM eclipse-temurin:17-jre
WORKDIR /app
COPY oquo-instance-creator-endpoint-0.0.1.jar app.jar
EXPOSE 8000
CMD ["java", "-jar", "app.jar", "--server.port=8000"]
