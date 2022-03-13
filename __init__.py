import os
import sys
import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
import pathlib
import re

bl_info = {
    "name": "Subtitle Import",
    "author": "tintwotin",
    "version": (0, 1, 0),
    "blender": (2, 92, 0),
    "description": "Import subtitles",
    "location": "Sequence Editor > Strip Menu > Import Subtitles",
    "warning": "",
    "tracker_url": "",
    "category": "Sequencer",
}

try:
    import pysubs2

    print("Installed: pysubs2")
except ImportError:
    print("Installing pysubs2...")
    import subprocess
    import bpy
    import os
    from pathlib import Path

    if bpy.app.version < (2, 92, 0):
        py_exec = bpy.app.binary_path_python
        subprocess.call([str(py_exec), "-m", "ensurepip", "--user"])
        subprocess.call([str(py_exec), "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.call([str(py_exec), "-m", "pip", "install", "--user", "pysubs2"])
    else:
        import sys

        py_exec = str(sys.executable)
        lib = os.path.join(Path(py_exec).parent.parent, "lib")
        subprocess.call([py_exec, "-m", "ensurepip", "--user"])
        subprocess.call([py_exec, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.call(
            [py_exec, "-m", "pip", "install", f"--target={str(lib)}", "pysubs2"]
        )
        import pysubs2
except PermissionError:
    print(
        "To install, restart Blender by right clicking the Blender icon and select Run as Administrator"
    )
except:
    print("Error installing pysubs2")


class SEQUENCER_OT_import_subtitles(Operator, ImportHelper):
    """Import subtitles"""

    bl_idname = "sequencer.import_subtitles"
    bl_label = "Import Subtitles"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = [".srt",".ass"]

    filter_glob: StringProperty(
        default='*.srt;*.ass;*.ssa;*.mpl2;*.tmp;*.vtt;*.microdvd',
        options={"HIDDEN"},
        maxlen=255,
    )

    def execute(self, context):
        render = bpy.context.scene.render
        fps = render.fps / render.fps_base
        fps_conv = fps / 1000

        sequence = bpy.data.scenes[0].sequence_editor
        top_channel = 0
        for i in range(len(sequence.sequences_all)):
            if top_channel < sequence.sequences_all[i].channel:
                top_channel = sequence.sequences_all[i].channel
        file = self.filepath
        if not file:
            return {"CANCELLED"}
        if pathlib.Path(file).is_file():
            if (
                pathlib.Path(file).suffix
                not in pysubs2.formats.FILE_EXTENSION_TO_FORMAT_IDENTIFIER
            ):
                print("Unable to extract subtitles from file")
                self.report({'INFO'}, "Unable to extract subtitles from file")
                return {"CANCELLED"}
        try:
            subs = pysubs2.load(self.filepath, fps=fps, encoding="utf-8")
        except:
            print("Import failed. Text encoding must be in UTF-8.")
            self.report({'INFO'}, "Import failed. Text encoding must be in UTF-8.")
            return {"CANCELLED"}
        if not subs:
            print("No file imported.")
            self.report({'INFO'}, "No file imported")
            return {"CANCELLED"}
        for line in subs:
            italics = False
            bold = False
            position = False
            pos = []
            line.text = line.text.replace("\\N", "\n")
            if r"<i>" in line.text or r"{\i1}" in line.text or r"{\i0}" in line.text:
                italics = True
                line.text = line.text.replace("<i>", "")
                line.text = line.text.replace("</i>", "")
                line.text = line.text.replace("{\\i0}", "")
                line.text = line.text.replace("{\\i1}", "")
            if r"<b>" in line.text or r"{\b1}" in line.text or r"{\b0}" in line.text:
                bold = True
                line.text = line.text.replace("<b>", "")
                line.text = line.text.replace("</b>", "")
                line.text = line.text.replace("{\\b0}", "")
                line.text = line.text.replace("{\\b1}", "")
            if r"{" in line.text:
                pos_trim = re.search(r'\{\\pos\((.+?)\)\}', line.text)
                print(pos_trim)
                pos_trim = pos_trim.group(1)
                print(pos_trim)
                pos = pos_trim.split(",")
                x = int(pos[0])/render.resolution_x
                y = (render.resolution_y-int(pos[1]))/render.resolution_y
                position = True
                line.text = re.sub(r'{.+?}', '', line.text)
                
            new_strip = sequence.sequences.new_effect(
                line.text,
                "TEXT",
                top_channel,
                frame_start=int(line.start * fps_conv),
                frame_end=int(line.end * fps_conv),
            )
            new_strip.text = line.text
            new_strip.wrap_width = 0.68
            new_strip.font_size = 48
            new_strip.location[1] = 0.2
            new_strip.align_x = 'CENTER'
            new_strip.align_y = "TOP"
            new_strip.use_shadow = True
            new_strip.use_box = True
            if position:
                new_strip.location[0] = x
                new_strip.location[1] = y
                new_strip.align_x = 'LEFT'
            if italics:
                new_strip.use_italic = True
            if bold:
                new_strip.use_bold = True
        return {"FINISHED"}


def import_subtitles(self, context):
    layout = self.layout
    layout.separator()
    layout.operator("sequencer.import_subtitles", icon="IMPORT")


classes = (SEQUENCER_OT_import_subtitles,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.SEQUENCER_MT_strip.append(import_subtitles)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.SEQUENCER_MT_strip.remove(import_subtitles)


if __name__ == "__main__":
    register()
