"""Package Reader - 读取 .smspkg 文件"""

from zipfile import ZipFile
import json


class PackageReader:
    def load(self, filename):
        """加载包并返回 manifest"""
        with ZipFile(filename, 'r') as z:
            manifest = json.loads(z.read("manifest.json").decode("utf-8"))
            return manifest

    def list_files(self, filename):
        """列出包中的所有文件"""
        with ZipFile(filename, 'r') as z:
            return sorted(z.namelist())

    def extract(self, filename, output_dir):
        """解包到指定目录"""
        with ZipFile(filename, 'r') as z:
            z.extractall(output_dir)
        return output_dir
