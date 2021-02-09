# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['Douyin_Win_Play.py'],
             pathex=['D:\\programs\\DouyinPlayer'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
a.datas+=[('dy.ico','dy.ico','data'),('list.jpg','list.jpg','data'),('quit.jpg','quit.jpg','data'),('save.jpg','save.jpg','data'),('setting.jpg','setting.jpg','data'),('next.jpg','next.jpg','data'),('back.jpg','back.jpg','data')]
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Douyin_Win_Play',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='dy.ico')
