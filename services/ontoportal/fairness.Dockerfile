# O'FAIRe (https://github.com/agroportal/fairness) built at a fixed commit.
#
# Same image as ontoportal_docker/config/fairness/Dockerfile, which clones the
# repository with 'git clone --branch "${FAIRNESS_REF}"' and therefore only
# accepts branches and tags. This version checks out the commit given in
# FAIRNESS_COMMIT, so that the assessment is reproducible.
#
# The build context is ontoportal_docker/config/fairness (set by start.sh), which
# provides entrypoint.sh and fairness-cache.

ARG MAVEN_IMAGE=maven:3.9-eclipse-temurin-11
ARG TOMCAT_IMAGE=tomcat:9.0-jre11-temurin

FROM ${MAVEN_IMAGE} AS build

ARG FAIRNESS_REPOSITORY=https://github.com/agroportal/fairness.git
ARG FAIRNESS_COMMIT

WORKDIR /src
RUN test -n "${FAIRNESS_COMMIT}" \
    && git clone "${FAIRNESS_REPOSITORY}" . \
    && git checkout --detach "${FAIRNESS_COMMIT}" \
    # the pom points at the deployment descriptor with Windows separators
    && sed -i 's|WebContent\\WEB-INF\\web.xml|WebContent/WEB-INF/web.xml|' pom.xml \
    && mvn -B -q clean package -DskipTests

FROM ${TOMCAT_IMAGE}

ARG FAIRNESS_COMMIT
LABEL org.opencontainers.image.source="https://github.com/agroportal/fairness" \
      org.opencontainers.image.revision="${FAIRNESS_COMMIT}"

# Deployed exploded as the ROOT webapp: the entrypoint writes the portal
# configuration into WEB-INF/classes before Tomcat starts
RUN rm -rf /usr/local/tomcat/webapps/*
COPY --from=build /src/target/fairness-assessment/ /usr/local/tomcat/webapps/ROOT/

COPY entrypoint.sh fairness-cache /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh /usr/local/bin/fairness-cache

EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["catalina.sh", "run"]
