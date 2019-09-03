from pathlib import Path

from invoke import Collection, task

BASE_CMD = ["pipenv", "run", "ansible-playbook"]

DEFAULT_ENV = {"OBJC_DISABLE_INITIALIZE_FORK_SAFETY": "YES"}
TASK_DEFAULT_ENVS = {
    "bootstrap": {
        "ANSIBLE_ASK_PASS": "true",
        "ANSIBLE_HOST_KEY_CHECKING": "false"
    }
}

ENV_ANSIBLE_REMOTE_USER = "ANSIBLE_REMOTE_USER"


def playbook_task_factory(name):
    @task(name=name,
          default=(name == "all"),
          help={
              "limit": "Limit hosts to an Ansible inventory pattern",
              "tags": "Limit tasks to an Ansible tag pattern",
              "user": "Username for remote task execution",
          })
    def _fn(c, limit=None, tags=None, user=None):
        cmd = BASE_CMD.copy()

        if limit is not None:
            cmd.append("--limit={}".format(limit))

        if tags is not None:
            cmd.append("--tags={}".format(tags))

        if user is not None:
            cmd.append("--extra-vars=\"ansible_user={}\"".format(user))

        env = DEFAULT_ENV.copy()

        if name in TASK_DEFAULT_ENVS:
            env.update(TASK_DEFAULT_ENVS[name])

        c.run(" ".join([*cmd, "ansible/{}.yml".format(name)]),
              env=env,
              pty=True)

    _fn.__doc__ = "Run the Ansible playbook at ansible/{}.yml".format(name)
    return _fn


playbooks = Collection("playbooks")

for f in Path.cwd().joinpath("ansible").glob("*.yml"):
    t = playbook_task_factory(f.stem)
    playbooks.add_task(t)
