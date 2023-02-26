import os
import sys
import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
import pathlib
import re

bl_info = {
    "name": "Subtitle Import and Translation",
    "author": "tintwotin",
    "version": (0, 2, 0),
    "blender": (3, 0, 0),
    "description": "Import and translate subtitles",
    "location": "Sequence Editor > Strip Menu > Import Subtitles",
    "warning": "",
    "tracker_url": "",
    "category": "Sequencer",
}


class SEQUENCER_OT_import_subtitles(Operator, ImportHelper):
    """Import subtitles"""

    bl_idname = "sequencer.import_subtitles"
    bl_label = "Import Subtitles"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = [".srt", ".ass"]

    filter_glob: StringProperty(
        default="*.srt;*.ass;*.ssa;*.mpl2;*.tmp;*.vtt;*.microdvd",
        options={"HIDDEN"},
        maxlen=255,
    )

    do_translate: BoolProperty(
        name="Translate Subtitle", description="Translate subtitle", default=False
    )

    translate_from: EnumProperty(
        name="From",
        description="Translate from",
        items=(
            ("auto", "Any language (detect)", ""),
            ("bg", "Bulgarian", ""),
            ("zh", "Chinese", ""),
            ("cs", "Czech", ""),
            ("da", "Danish", ""),
            ("nl", "Dutch", ""),
            ("en", "English", ""),  # Only usable for source language
            # ("en-US", "English (American)", ""),  # Only usable for destination language
            # ("en-GB", "English (British)", ""),  # Only usable for destination language
            ("et", "Estonian", ""),
            ("fi", "Finnish", ""),
            ("fr", "French", ""),
            ("de", "German", ""),
            ("el", "Greek", ""),
            ("hu", "Hungarian", ""),
            ("id", "Indonesian", ""),
            ("it", "Italian", ""),
            ("ja", "Japanese", ""),
            ("lv", "Latvian", ""),
            ("lt", "Lithuanian", ""),
            ("pl", "Polish", ""),
            ("pt", "Portuguese", ""),  # Only usable for source language
            # ("pt-PT", "Portuguese", ""),  # Only usable for destination language
            # ("pt-BR", "Portuguese (Brazilian)", ""),  # Only usable for destination language
            ("ro", "Romanian", ""),
            ("ru", "Russian", ""),
            ("sk", "Slovak", ""),
            ("sl", "Slovenian", ""),
            ("es", "Spanish", ""),
            ("sv", "Swedish", ""),
            ("tr", "Turkish", ""),
            ("uk", "Ukrainian", ""),
        ),
        default="auto",
    )

    translate_to: EnumProperty(
        name="To",
        description="Translate to",
        items=(
            # ("auto", "Any language (detect)", ""),
            ("bg", "Bulgarian", ""),
            ("zh", "Chinese", ""),
            ("cs", "Czech", ""),
            ("da", "Danish", ""),
            ("nl", "Dutch", ""),
            # ("en", "English", ""),  # Only usable for source language
            ("en-US", "English (American)", ""),  # Only usable for destination language
            ("en-GB", "English (British)", ""),  # Only usable for destination language
            ("et", "Estonian", ""),
            ("fi", "Finnish", ""),
            ("fr", "French", ""),
            ("de", "German", ""),
            ("el", "Greek", ""),
            ("hu", "Hungarian", ""),
            ("id", "Indonesian", ""),
            ("it", "Italian", ""),
            ("ja", "Japanese", ""),
            ("lv", "Latvian", ""),
            ("lt", "Lithuanian", ""),
            ("pl", "Polish", ""),
            # ("pt", "Portuguese", ""),  # Only usable for source language
            ("pt-PT", "Portuguese", ""),  # Only usable for destination language
            (
                "pt-BR",
                "Portuguese (Brazilian)",
                "",
            ),  # Only usable for destination language
            ("ro", "Romanian", ""),
            ("ru", "Russian", ""),
            ("sk", "Slovak", ""),
            ("sl", "Slovenian", ""),
            ("es", "Spanish", ""),
            ("sv", "Swedish", ""),
            ("tr", "Turkish", ""),
            ("uk", "Ukrainian", ""),
        ),
        default="en-US",
    )

    def execute(self, context):
        if self.do_translate:
            print(self.translate_from)
            try:
                from srtranslator import SrtFile
                from srtranslator.translators.deepl import DeeplTranslator
            except ModuleNotFoundError:
                import site
                import subprocess
                import sys

                app_path = site.USER_SITE
                if app_path not in sys.path:
                    sys.path.append(app_path)
                pybin = sys.executable  # bpy.app.binary_path_python # Use for 2.83

                print("Ensuring: pip")
                try:
                    subprocess.call([pybin, "-m", "ensurepip"])
                except ImportError:
                    pass
                self.report({"INFO"}, "Installing: srtranslator module.")
                print("Installing: srtranslator module")
                subprocess.check_call([pybin, "-m", "pip", "install", "srtranslator"])
                try:
                    from srtranslator import SrtFile
                    from srtranslator.translators.deepl import DeeplTranslator

                    self.report({"INFO"}, "Detected: srtranslator module.")
                    print("Detected: srtranslator module")
                except ModuleNotFoundError:
                    print("Installation of the srtranslator module failed")
                    self.report(
                        {"INFO"},
                        "Installing srtranslator module failed! Try to run Blender as administrator.",
                    )
                    return {"CANCELLED"}
            file = self.filepath
            if not file:
                return {"CANCELLED"}
                print("Invalid file")
                self.report({"INFO"}, "Invalid file")
            translator = DeeplTranslator()
            if pathlib.Path(file).is_file():
                print("Translating. Please Wait.")
                self.report({"INFO"}, "Translating. Please Wait.")
                srt = SrtFile(file)
                srt.translate(translator, self.translate_from, self.translate_to)

                # Making the result subtitles prettier
                srt.wrap_lines()

                srt.save(f"{os.path.splitext(file)[0]}_translated.srt")
                translator.quit()
                print("Translating finished.")
                self.report({"INFO"}, "Translating finished.")
        try:
            import pysubs2
        except ModuleNotFoundError:
            import site
            import subprocess
            import sys

            app_path = site.USER_SITE
            if app_path not in sys.path:
                sys.path.append(app_path)
            pybin = sys.executable  # bpy.app.binary_path_python # Use for 2.83

            print("Ensuring: pip")
            try:
                subprocess.call([pybin, "-m", "ensurepip"])
            except ImportError:
                pass
            self.report({"INFO"}, "Installing: pysubs2 module.")
            print("Installing: pysubs2 module")
            subprocess.check_call([pybin, "-m", "pip", "install", "pysubs2"])
            try:
                import pysubs2
            except ModuleNotFoundError:
                print("Installation of the pysubs2 module failed")
                self.report(
                    {"INFO"},
                    "Installing pysubs2 module failed! Try to run Blender as administrator.",
                )
                return {"CANCELLED"}
        render = bpy.context.scene.render
        fps = render.fps / render.fps_base
        fps_conv = fps / 1000

        editor = bpy.data.scenes[0].sequence_editor
        sequences = bpy.context.sequences
        if not sequences:
            addSceneChannel = 1
        else:
            channels = [s.channel for s in sequences]
            channels = sorted(list(set(channels)))
            empty_channel = channels[-1] + 1
            addSceneChannel = empty_channel
        file = self.filepath
        if self.do_translate:
            file = f"{os.path.splitext(file)[0]}_translated.srt"
        if not file:
            return {"CANCELLED"}
        if pathlib.Path(file).is_file():
            if (
                pathlib.Path(file).suffix
                not in pysubs2.formats.FILE_EXTENSION_TO_FORMAT_IDENTIFIER
            ):
                print("Unable to extract subtitles from file")
                self.report({"INFO"}, "Unable to extract subtitles from file")
                return {"CANCELLED"}
        try:
            subs = pysubs2.load(file, fps=fps, encoding="utf-8")
        except:
            print("Import failed. Text encoding must be in UTF-8.")
            self.report({"INFO"}, "Import failed. Text encoding must be in UTF-8.")
            return {"CANCELLED"}
        if not subs:
            print("No file imported.")
            self.report({"INFO"}, "No file imported")
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
                pos_trim = re.search(r"\{\\pos\((.+?)\)\}", line.text)
                print(pos_trim)
                pos_trim = pos_trim.group(1)
                print(pos_trim)
                pos = pos_trim.split(",")
                x = int(pos[0]) / render.resolution_x
                y = (render.resolution_y - int(pos[1])) / render.resolution_y
                position = True
                line.text = re.sub(r"{.+?}", "", line.text)
            new_strip = editor.sequences.new_effect(
                line.text,
                "TEXT",
                addSceneChannel,
                frame_start=int(line.start * fps_conv),
                frame_end=int(line.end * fps_conv),
            )
            new_strip.text = line.text
            new_strip.wrap_width = 0.68
            new_strip.font_size = 48
            new_strip.location[1] = 0.2
            new_strip.align_x = "CENTER"
            new_strip.align_y = "TOP"
            new_strip.use_shadow = True
            new_strip.use_box = True
            if position:
                new_strip.location[0] = x
                new_strip.location[1] = y
                new_strip.align_x = "LEFT"
            if italics:
                new_strip.use_italic = True
            if bold:
                new_strip.use_bold = True
        return {"FINISHED"}


class SEQUENCER_OT_copy_textprops_to_selected(Operator):
    """Copy properties from active text strip to selected text strips"""

    bl_idname = "sequencer.copy_textprops_to_selected"
    bl_label = "Copy Properties to Selected"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        current_scene = bpy.context.scene
        try:
            active = current_scene.sequence_editor.active_strip
        except AttributeError:
            self.report({"INFO"}, "No active strip selected")
            return {"CANCELLED"}
        for strip in context.selected_sequences:
            if strip.type == active.type == "TEXT":
                strip.wrap_width = active.wrap_width
                strip.font = active.font
                strip.use_italic = active.use_italic
                strip.use_bold = active.use_bold
                strip.font_size = active.font_size
                strip.color = active.color
                strip.use_shadow = active.use_shadow
                strip.shadow_color = active.shadow_color
                strip.use_box = active.use_box
                strip.box_color = active.box_color
                strip.box_margin = active.box_margin
                strip.location[0] = active.location[0]
                strip.location[1] = active.location[1]
                strip.align_x = active.align_x
                strip.align_y = active.align_y
        return {"FINISHED"}


def import_subtitles(self, context):
    layout = self.layout
    layout.separator()
    layout.operator("sequencer.import_subtitles", icon="IMPORT")


def copyto_panel_append(self, context):
    strip = context.active_sequence_strip
    strip_type = strip.type
    if strip_type == "TEXT":
        layout = self.layout
        layout.operator(SEQUENCER_OT_copy_textprops_to_selected.bl_idname)


classes = (
    SEQUENCER_OT_import_subtitles,
    SEQUENCER_OT_copy_textprops_to_selected,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.SEQUENCER_MT_strip.append(import_subtitles)
    bpy.types.SEQUENCER_PT_effect.append(copyto_panel_append)


def unregister():
    bpy.types.SEQUENCER_PT_effect.remove(copyto_panel_append)
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.SEQUENCER_MT_strip.remove(import_subtitles)


if __name__ == "__main__":
    register()
