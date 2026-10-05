# SAST

```bash
docker run --rm -v "$PWD:/src" semgrep/semgrep   semgrep --config p/python /src/app
```

SonarQube can be added as a separate quality gate using the test coverage produced by CI.
