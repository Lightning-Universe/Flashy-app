import os
import sys

sys.path.append(os.path.dirname(__file__))

from lightning import LightningApp, LightningFlow  # noqa: E402
from lightning.frontend import StaticWebFrontend  # noqa: E402
from lightning.storage.drive import Drive  # noqa: E402

from flashy.components.file_server import FileServer  # noqa: E402
from flashy.hpo_manager import HPOManager  # noqa: E402


class ReactUI(LightningFlow):
    def configure_layout(self):
        return StaticWebFrontend(
            os.path.join(os.path.dirname(__file__), "flashy", "ui", "build")
        )


class Flashy(LightningFlow):
    """The root flow for the `Flashy` app."""

    def __init__(self):
        super().__init__()

        self.datasets = Drive("lit://datasets")
        self.checkpoints = Drive("lit://checkpoints", allow_duplicates=True)

        self.ui = ReactUI()
        self.hpo = HPOManager(self.datasets, self.checkpoints)

        self.file_upload = FileServer(self.datasets, run_once=True, parallel=True)
        self.file_upload_url: str = ""

        self.checkpoints_server = FileServer(
            self.datasets, run_once=True, parallel=True
        )
        self.checkpoints_server_url: str = ""

    def run(self):
        self.file_upload_url = self.file_upload.url
        self.file_upload.run()

        self.checkpoints_server_url = self.checkpoints_server.url
        self.checkpoints_server.run()

        self.hpo.run()

    def configure_layout(self):
        return [
            {"name": "Flashy", "content": self.ui},
        ]


app = LightningApp(Flashy(), debug=False)
