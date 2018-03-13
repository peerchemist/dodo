from setuptools import setup

setup(name='dodo',
      version='0.43',
      description='Simple CLI cryptocurrency exchange client based of cryptotik library.',
      keywords=['cryptocurrency', 'trading', 'exchange', 'client'],
      url='https://github.com/peerchemist/dodo',
      packages=['dodo'],
      author='Peerchemist',
      author_email='peerchemist@protonmail.ch',
      license='BSD',
      install_requires=['cryptotik', 'fire', 'keyring', 'appdirs'],
      entry_points={
          'console_scripts': [
              'dodo = dodo.__main__:main'
                  ]}
      )
