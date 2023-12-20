import os
import shutil
import zipfile
from datetime import datetime
from tqdm import tqdm

from modules_src.config import version


def zip_compress(to_zip, save_zip_name):  # save_zip_name是带目录的，也可以不带就是当前目录
    # 1.先判断输出save_zip_name的上级是否存在(判断绝对目录)，否则创建目录
    save_zip_dir = os.path.split(os.path.abspath(save_zip_name))[0]  # save_zip_name的上级目录
    print('正在将 %s 压缩为 %s 请等待……' % (to_zip, save_zip_name))
    if not os.path.exists(save_zip_dir):
        os.makedirs(save_zip_dir)
        print('创建新目录%s' % save_zip_dir)
    f = zipfile.ZipFile(os.path.abspath(save_zip_name), 'w', zipfile.ZIP_DEFLATED)
    # 2.判断要被压缩的to_zip是否目录还是文件，是目录就遍历操作，是文件直接压缩
    if not os.path.isdir(os.path.abspath(to_zip)):  # 如果不是目录,那就是文件
        if os.path.exists(os.path.abspath(to_zip)):  # 判断文件是否存在
            f.write(to_zip)
            f.close()
            print('%s 压缩为 %s 完成！' % (to_zip, save_zip_name))
        else:
            print('%s 文件不存在' % os.path.abspath(to_zip))
    else:
        if os.path.exists(os.path.abspath(to_zip)):  # 判断目录是否存在，遍历目录
            zipList = []
            for dir, subdirs, files in os.walk(to_zip):  # 遍历目录，加入列表
                for fileItem in files:
                    zipList.append(os.path.join(dir, fileItem))
                    # print('a',zipList[-1])
                for dirItem in subdirs:
                    zipList.append(os.path.join(dir, dirItem))
                    # print('b',zipList[-1])
            # 读取列表压缩目录和文件
            for i in zipList:
                f.write(i, i.replace(to_zip, ''))  # replace是减少压缩文件的一层目录，即压缩文件不包括to_zip这个目录
                # print('%s压缩到%s'%(i,save_zip_name))
            f.close()
            print('%s 压缩为 %s 完成！' % (to_zip, save_zip_name))
        else:
            print('%s 文件夹不存在' % os.path.abspath(to_zip))


def countFiles(root_path):
    assert os.path.exists(root_path)
    total_files = 0
    item_list = os.listdir(root_path)
    if len(item_list) == 0:
        return 0
    for item in item_list:
        next_path = os.path.join(root_path, item)
        if item == "__pycache__":  # 判断是否pycache文件
            pass
        else:
            if os.path.isfile(next_path):
                total_files += 1
            else:
                total_files += countFiles(next_path)
    return total_files


def deep_copy_dirs_tqdm(from_file, to_file):
    file_num = countFiles(from_file)
    pbar = tqdm(total=file_num)

    def copydirs(_from_file, _to_file):
        if not os.path.exists(_to_file):  # 如不存在目标目录则创建
            os.makedirs(_to_file)
        files = os.listdir(_from_file)  # 获取文件夹中文件和目录列表
        for f in files:
            if f == "__pycache__":  # 判断是否pycache文件
                pass
            else:
                if os.path.isdir(_from_file + '/' + f):  # 判断是否是文件夹
                    copydirs(_from_file + '/' + f, _to_file + '/' + f)  # 递归调用本函数
                else:
                    shutil.copy(_from_file + '/' + f, _to_file + '/' + f)  # 拷贝文件
                    pbar.update(1)

    copydirs(from_file, to_file)
    pbar.close()


cmd_nuitka = "                                     \
             nuitka3                               \
             --standalone                          \
             --mingw64                             \
             --nofollow-imports                    \
             --show-memory                         \
             --show-progress                       \
             --windows-uac-admin                   \
             --plugin-enable=qt-plugins            \
             --include-qt-plugins=sensible,styles  \
             --windows-icon-from-ico=conhost.ico   \
             --output-dir=output                   \
             main.py                               \
             "

cmd_nuitka_disable_console = "                     \
             nuitka3                               \
             --standalone                          \
             --mingw64                             \
             --nofollow-imports                    \
             --show-memory                         \
             --show-progress                       \
             --plugin-enable=numpy                 \
             --plugin-enable=qt-plugins            \
             --windows-uac-admin                   \
             --include-qt-plugins=sensible,styles  \
             --windows-icon-from-ico=conhost.ico   \
             --output-dir=output                   \
             --windows-disable-console             \
             main.py                               \
             "


def auto_build_pyd(path_: str):
    def is_ignore(name_):
        ignore_list = ["__init__", "__pycache", ".pyd", ".pyc", ".dll", ".DLL", ".ui"]
        result = True
        for ignore in ignore_list:
            if ignore in name_:
                result = False
            if ".py" not in name_:
                return False
        return result

    for root, dirs, files in os.walk(path_, topdown=False):
        for name in files:
            if is_ignore(name) and "__pycache__" not in root:
                cmd_pyd = "nuitka3 --mingw64 --module --remove-output --no-pyi-file --output-dir=%s %s" % (
                    "output/dependence/" + root, os.path.join(root, name))
                os.system(cmd_pyd)


os.system('chcp 65001')
shutil.rmtree('output/dist/main', ignore_errors=True)
shutil.rmtree('output/build', ignore_errors=True)
shutil.rmtree('output/dist_console/main', ignore_errors=True)
shutil.rmtree('output/build_console', ignore_errors=True)


print("开始编译模块！")


#使用nuitka编译
nuitka_modules_cmds = [
    "nuitka3 --mingw64 --module --remove-output --no-pyi-file --output-dir=output/dependence/modules "
    "modules_src/dm_plugin.py",
    "nuitka3 --mingw64 --module --remove-output --no-pyi-file --output-dir=output/dependence/modules "
    "modules_src/baidu_api.py",
    "nuitka3 --mingw64 --module --remove-output --no-pyi-file --output-dir=output/dependence/modules "
    "modules/del_self.py",
]

for cmd in nuitka_modules_cmds:
    os.system(cmd)

print("模块编译完成！")
print("开始编译入口文件！")

cmd_pyinstaller = "pyinstaller main.spec --clean --noconfirm --distpath ./output/dist --workpath ./output/build"
cmd_pyinstaller_console = "pyinstaller main_console.spec --clean --noconfirm --distpath ./output/dist_console " \
                          "--workpath ./output/build_console "

os.system(cmd_pyinstaller)
os.system(cmd_pyinstaller_console)

print("入口文件编译完成！")
print("复制依赖文件...")

pic_path = os.path.abspath(r'position_pic/')  # 项目内部文件
dependence_path = os.path.abspath(r'output/dependence/')  # 项目外部依赖

target_path = os.path.abspath(r'output/dist/main')  # 目标文件夹
target_console_path = os.path.abspath(r'output/dist_console/main')

# 删除和重新拷贝comtypes
shutil.rmtree('output/dependence/comtypes', ignore_errors=True)
deep_copy_dirs_tqdm('D:\\work\yectc_single\\venv\\Lib\\site-packages\\comtypes', 'output/dependence/comtypes')

deep_copy_dirs_tqdm(dependence_path, target_path)  # 复制外部依赖到目标文件夹
deep_copy_dirs_tqdm(dependence_path, target_console_path)  # 复制外部依赖到目标文件夹

deep_copy_dirs_tqdm(pic_path, target_path + "/position_pic")  # 复制内部依赖，注意最后的路径要添加目标文件夹"/modules"
deep_copy_dirs_tqdm(pic_path, target_console_path + "/position_pic")  # 复制内部依赖，注意最后的路径要添加目标文件夹"/modules"

print("复制完成！")

print("打包压缩文件")

shutil.copy('util/num', 'output/dependence/util/num')
shutil.copy('util/chinese', 'output/dependence/util/chinese')
shutil.copy('util/dm.dll', 'output/dependence/util/dm.dll')
shutil.copy('util/DmReg.dll', 'output/dependence/util/DmReg.dll')

cmd_enigma = '"C:\Program Files (x86)\Enigma Virtual Box\enigmavbconsole.exe" D:\work\yectc_single\output\exe_dir.evb'
cmd_enigma_console = '"C:\Program Files (x86)\Enigma Virtual Box\enigmavbconsole.exe" ' \
                     'D:\work\yectc_single\output\exe_dir_console.evb '
os.system(cmd_enigma)
os.system(cmd_enigma_console)
#
print("删除多余文件")
rm_path = [
    'output/dist/main/altgraph-0.17.2.dist-info',
    'output/dist/main/pyinstaller-4.5.1.dist-info',
    'output/dist/main/setuptools-57.0.0.dist-info',
    'output/dist/main/wheel-0.36.2.dist-info',

    'output/dist_console/main/altgraph-0.17.2.dist-info',
    'output/dist_console/main/pyinstaller-4.5.1.dist-info',
    'output/dist_console/main/setuptools-57.0.0.dist-info',
    'output/dist_console/main/wheel-0.36.2.dist-info',

    'output/dist/main/util',
    'output/dist/main/modules',
    'output/dist/main/position_pic',

    'output/dist_console/main/util',
    'output/dist_console/main/modules',
    'output/dist_console/main/position_pic',

]
for path in rm_path:
    shutil.rmtree(path, ignore_errors=True)

remove_path = [
    'output/dist/main/main.exe',
    'output/dist/main/opengl32sw.dll',
    'output/dist/main/cv2/opencv_videoio_ffmpeg453.dll',

    'output/dist_console/main/main.exe',
    'output/dist_console/main/opengl32sw.dll',
    'output/dist_console/main/cv2/opencv_videoio_ffmpeg453.dll',

    'output/dependence/util/num',
    'output/dependence/util/chinese',
    'output/dependence/util/dm.dll',
    'output/dependence/util/DmReg.dll',
]
try:
    for path in remove_path:
        os.remove(path)
    print("多余文件删除完成！")
except FileNotFoundError as e:
    print(e)

shutil.move('output/dist/main.exe', 'output/dist/main/main.exe')
shutil.move('output/dist_console/main.exe', 'output/dist_console/main/main.exe')
print(datetime.now(), "编译完成！")

zip_compress('output/dist/main', 'output/main_' + version + '.zip')
zip_compress('output/dist_console/main', 'output/main_console_' + version + '.zip')

