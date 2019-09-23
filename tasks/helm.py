import tarfile
from pathlib import Path

import yaml
from invoke import Collection, task


@task(help={
    "chart": "Helm chart to fetch (required)",
    "repo": "Chart repository URL from which to fetch the chart",
    "username": "Username for the chart repository",
    "password": "Password for the chart repository"
},
      name="fetch",
      positional=["chart"])
def helm_fetch(c, chart, repo=None, username=None, password=None):
    """Fetch a Helm chart

    Example:

        hfi helm.fetch stable/traefik
    """
    cmd = ["helm", "fetch"]

    if repo is not None:
        cmd += ["--repo", repo]
        chart_base = chart
    else:
        repo, chart_base = chart.split("/")

    if username is not None:
        cmd += ["--username", username]

    if password is not None:
        cmd += ["--password", password]

    cmd += [chart]
    c.run(" ".join(cmd))


@task(help={
    "chart": "Helm chart to extract values.yaml from",
    "cluster": "Target cluster for the generated manifests"
},
      name="values")
def helm_values(c, chart, cluster="common"):
    """Extract the values.yaml file from a fetched Helm chart to
    values/chartname.yml

    Example:

        hfi helm.fetch stable/traefik
        hfi helm.values traefik
    """
    cwd = Path.cwd()
    values = cwd.joinpath("k8s", ".values", cluster)
    values.mkdir(exist_ok=True, parents=True)

    chart_archive = tarfile.open(list(cwd.glob("{}-*.tgz".format(chart)))[-1])

    with open(values.joinpath("{}.yml".format(chart)), 'wb') as file:
        buf = chart_archive.extractfile("{}/values.yaml".format(chart))

        if buf is not None:
            file.write(buf.read())


@task(help={
    "chart": "Helm chart to generate manifests of from templates",
    "cluster": "Target cluster for the generated manifests",
    "dir": "Generate templates into directory instead of single file",
    "name": "Name of the installation",
    "namespace": "Target namespace for the manifests"
},
      name="template")
def helm_template(c,
                  chart,
                  cluster="common",
                  dir=False,
                  name=None,
                  namespace="default"):
    """Generate a manifest from a fetch Helm chart and (if present) its
    extracted and modified values.yaml file

    Example:

        hfi helm.fetch stable/traefik
        hfi helm.values traefik
        hfi helm.template traefik
    """
    cwd = Path.cwd()

    try:
        chart_archive = list(cwd.glob("{}-*.tgz".format(chart)))[-1]
    except IndexError:
        print("No such chart exists, try helm.fetch first")
        exit(1)

    cmd = ["helm", "template", chart_archive.name]

    values = cwd.joinpath("k8s", ".values", cluster, "{}.yml".format(chart))
    if values.is_file():
        cmd += ["--values", str(values)]

    if name is None:
        name = chart

    cmd += ["--name", name]
    cmd += ["--namespace", namespace]

    base_dir = cwd.joinpath("k8s", cluster, namespace)

    if dir:
        output_dir = cwd.joinpath("k8s", cluster, namespace, name)
        output_dir.mkdir(exist_ok=True, parents=True)
        cmd += ["--output-dir", "{}".format(output_dir)]

    proc = c.run(" ".join(cmd), hide="out")
    manifest = cwd.joinpath("k8s", cluster, namespace, "{}.yml".format(name))

    if not dir:
        with open(manifest, "w") as file:
            for doc in yaml.safe_load_all(proc.stdout):
                print(doc)
                if doc is None:
                    continue

                if doc["kind"] == "List":
                    for d in doc["items"]:
                        _write_manifest(d, file, namespace, name, chart)
                    continue

                _write_manifest(doc, file, namespace, name, chart)


def _write_manifest(doc, file, namespace, name, chart):
    doc["metadata"].setdefault("namespace", namespace)

    for key in ["app", "chart", "heritage", "release"]:
        try:
            del doc["metadata"]["labels"][key]
        except KeyError:
            pass

    doc["metadata"].setdefault("labels", {})
    doc["metadata"]["labels"].setdefault("app.kubernetes.io/name",
                                            chart)
    doc["metadata"]["labels"].setdefault(
        "app.kubernetes.io/instance", name)

    yaml.dump(doc, file, explicit_start=True)


@task(help={"chart": "Helm chart to fetch and extract values.yaml from"},
      name="default",
      default=True)
def helm_default(c, chart):
    """Fetch a Helm chart and extract its values.yaml file to
    values/chartname.yaml

    Example:

        hfi helm stable/traefik
    """
    repo, chart_base = chart.split("/")
    helm_fetch(c, chart)
    helm_values(c, chart_base)


helm = Collection("helm")
helm.add_task(helm_default)
helm.add_task(helm_fetch)
helm.add_task(helm_template)
helm.add_task(helm_values)
