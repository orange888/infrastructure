import tarfile
from pathlib import Path

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

        inv helm.fetch stable/traefik
    """
    cmd = ["helm", "fetch"]
    args = []

    if repo is not None:
        args.extend(["--repo", repo])
        chart_base = chart
    else:
        repo, chart_base = chart.split("/")

    if username is not None:
        args.extend(["--username", username])

    if password is not None:
        args.extend(["--password", password])

    cmd.extend(args)
    cmd.append(chart)
    c.run(" ".join(cmd))


@task(help={"chart": "Helm chart to extract values.yaml from"}, name="values")
def helm_values(c, chart):
    """Extract the values.yaml file from a fetched Helm chart to
    values/chartname.yml

    Example:

        inv helm.fetch stable/traefik
        inv helm.values traefik
    """
    cwd = Path.cwd()
    values = cwd.joinpath("values")
    values.mkdir(exist_ok=True)

    chart_archive = tarfile.open(list(cwd.glob("{}-*.tgz".format(chart)))[-1])

    with open(values.joinpath("{}.yml".format(chart)), 'wb') as file:
        buf = chart_archive.extractfile("{}/values.yaml".format(chart))

        if buf is not None:
            file.write(buf.read())


@task(help={"chart": "Helm chart to fetch and extract values.yaml from"},
      name="default",
      default=True)
def helm_default(c, chart):
    """Fetch a Helm chart and extract its values.yaml file to
    values/chartname.yaml

    Example:

        inv helm stable/traefik
    """
    repo, chart_base = chart.split("/")
    helm_fetch(c, chart)
    helm_values(c, chart_base)


helm = Collection("helm")
helm.add_task(helm_default)
helm.add_task(helm_fetch)
helm.add_task(helm_values)
