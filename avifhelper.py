import os.path
from tkinter import *
from tkinter.ttk import *

from tkinter import filedialog
from tkinter import messagebox
from tkinterdnd2 import *

import subprocess
import re


APP_DIR = os.path.dirname(__file__)
APP_NAME = 'AVIF Helper'
APP_VERSION = '0.0.5'
MAX_PIXELS = 1600*1200


root = Tk()
root.title(APP_NAME + ' ' + APP_VERSION)
root.resizable(False, False)
root.iconbitmap(os.path.join(APP_DIR, 'avif-logo-rgb.svg.ico'))  # https://redketchup.io/icon-editor

original_image_filename = StringVar(root, '')
final_quality_setting = IntVar(root, 50)
target_file_size_string = StringVar(root, "42000")
resize_enable = IntVar(root, 1)


def show_open_dialog():
    filetypes = (
        ('All Images', '*.jpg *.jpeg *.png'),
        ('JPG', '*.jpg'),
        ('JPEG', '*.jpeg'),
        ('PNG', '*.png'),
        ('All files', '*.*')
    )

    filename = filedialog.askopenfilename(filetypes=filetypes)
    set_source_image(filename)


def handle_drop_file(event):
    if event.data:
        files = logger.tk.splitlist(event.data)
        for f in files:
            if os.path.exists(f):
                set_source_image(f)
                break


def set_source_image(filename):
    original_image_filename.set(filename)

    if filename != '':
        log('File selected: ' + filename + '\n')
        btn2['state'] = 'active'
    else:
        btn2['state'] = 'disabled'

    btn3['state'] = 'disabled'


def my_subprocess_run(cmd):
    # set stderr and stdin
    # and set startupinfo, and env
    # and hide the window
    # all to make PyInstaller play nicely
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                            startupinfo=si, env=os.environ).stdout
    return output.decode('utf-8')


def compress_image(src_filename, dest_filename, quality=50):
    cmd = [
        os.path.join(APP_DIR, 'magick.exe'),
        src_filename,
    ]

    if resize_enable.get() == 1:
        cmd.extend([
            '-resize', str(MAX_PIXELS) + '@^>'
        ])

    cmd.extend([
        '-quality', str(quality),
        '-verbose',
        dest_filename
    ])

    output = my_subprocess_run(cmd)

    if '.avif' not in output:
        log('FAILED, Processing Image: ' + repr(output) + '\n\n')
        return None

    matches = re.search(r' (\d+)B ', output)

    if matches is None:
        log('FAILED, No Match: ' + repr(matches) + '\n\n')

    return int(matches.group(1))


def find_optimal_settings():
    if btn2['state'] == 'disabled':
        return

    btn1['state'] = 'disabled'
    btn2['state'] = 'disabled'
    btn3['state'] = 'disabled'
    root.update()

    possible_quality = [70, 60, 50, 40, 35, 30, 25, 22, 19, 16, 13, 10, 7]
    target_file_size = int(target_file_size_string.get())

    for quality in possible_quality:

        file_size = compress_image(original_image_filename.get(), APP_DIR + '/tmp.avif', quality)

        if os.path.exists(APP_DIR + '/tmp.avif'):
            os.unlink(APP_DIR + '/tmp.avif')

        if file_size is None:
            break

        if file_size < target_file_size:
            log('Quality=' + str(quality) + '  Size=' + str(file_size) + ' bytes  Done!\n\n')
            final_quality_setting.set(quality)
            btn3['state'] = 'active'
            break
        else:
            log('Quality=' + str(quality) + '  Size=' + str(file_size) + ' bytes\n')

        root.update()

    btn1['state'] = 'active'
    btn2['state'] = 'active'


def build_reasonable_destination_filename(original_filename):
    # create a reasonable filename to save as
    directory, filename_and_ext = os.path.split(original_filename)
    just_filename, extension = os.path.splitext(filename_and_ext)
    return just_filename + '.avif'


def save_avif():
    if btn3['state'] == 'disabled':
        return

    dest_filename = filedialog.asksaveasfilename(
        filetypes=(('AVIF', '*.avif'),),
        defaultextension=".avif",
        initialfile=build_reasonable_destination_filename(original_image_filename.get()))

    if dest_filename != "":
        log("Dest filename " + repr(dest_filename))
        file_size = compress_image(original_image_filename.get(), dest_filename, final_quality_setting.get())
        if file_size is None:
            log('Error Saving!?\n')
        else:
            log('File Saved: ' + str(file_size) + ' bytes saved to ' + dest_filename + '\n\n')


def show_about_dialog():
    messagebox.showinfo('About', APP_NAME + ' ' + APP_VERSION + '\n\n' + 'This program uses ImageMagick for image '
                        + 'processing\nhttps://imagemagick.org/\n\n'
                        + 'Icon Copyright ©2019 The Alliance for Open Media\n\n')


if __name__ == '__main__':

    top_frame = Frame(root, height=400)
    top_frame.grid(row=0, column=0, padx=10, pady=5)

    logger = Text(top_frame)
    logger_scrollbar = Scrollbar(top_frame, orient='vertical', command=logger.yview)

    logger.configure(yscrollcommand=logger_scrollbar.set)
    logger_scrollbar.pack(side='right', fill='y')
    logger.pack()  # side='left', fill='both', expand=True)

    logger.drop_target_register(DND_FILES)
    logger.dnd_bind('<<Drop>>', handle_drop_file)

    def log(s):
        logger.insert(END, s)
        logger.see('end')

    log('Running in ' + APP_DIR + '\n\n')
    log('Select a JPEG, or PNG image and this program will find a quality setting\n')
    log('that results in a file <= 42,000 bytes (< 120sec in EasyPal).\n\n')
    log('Now supports drag and drop!\n\n')
    log('This program using ImageMagick for the actual conversion\n\n')
    log('Images larger than 1600x1200 are scaled down before compression\n\n')
    log('CTRL+O to Open, CTRL+F to Find Quality, CTRL+S to Save, and CTRL+Q to quit\n\n')

    bottom_frame = Frame(root)
    bottom_frame.grid(row=1, column=0, padx=10, pady=10)

    #
    resize_frame = Frame(bottom_frame)
    resize_frame.grid(row=0, column=0, padx=10, pady=5)

    resize_checkbox = Checkbutton(resize_frame, text="Auto Resize", onvalue=1, offvalue=0, variable=resize_enable)
    resize_checkbox.pack(side=LEFT)

    #
    target_frame = Frame(bottom_frame)
    target_frame.grid(row=1, column=0, padx=10)

    Label(target_frame, text="Target File Size: ").pack(side=LEFT)  # .grid(row=0, column=0, padx=10)

    target_size_spinbox = Spinbox(target_frame, width=8, from_=20000, to=80000,
                                  textvariable=target_file_size_string, increment=1000.0)
    target_size_spinbox.pack(side=LEFT)

    #
    button_frame = Frame(bottom_frame)
    button_frame.grid(row=0, column=1, columnspan=2, padx=10)

    btn1 = Button(button_frame, text='Select Image', command=show_open_dialog)
    btn1.grid(row=0, column=0, padx=10)

    btn2 = Button(button_frame, text='Find Optimal Quality', command=find_optimal_settings)
    btn2.grid(row=0, column=1, padx=10)
    btn2['state'] = 'disabled'

    btn3 = Button(button_frame, text='Save AVIF', command=save_avif)
    btn3.grid(row=0, column=2, padx=10)
    btn3['state'] = 'disabled'

    btn_about = Button(button_frame, text='About', command=show_about_dialog)
    btn_about.grid(row=0, column=3, padx=10)

    root.bind('<Control-o>', lambda event: show_open_dialog())
    root.bind('<Control-s>', lambda event: save_avif())
    root.bind('<Control-f>', lambda event: find_optimal_settings())
    root.bind('<Control-q>', lambda event: root.quit())
    root.mainloop()
