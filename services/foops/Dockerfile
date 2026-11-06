FROM eclipse-temurin:17-jre
WORKDIR /app
COPY fair_ontologies-0.4.0.jar app.jar
EXPOSE 8002
CMD ["java", "-jar", "app.jar", "--server.port=8002"]
