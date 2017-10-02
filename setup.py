from setuptools import setup

setup(name='dodo',
      version='0.1',
      description='Simple CLI cryptocurrency exchange client based of cryptotik library.',
      keywords=['cryptocurrency', 'trading', 'exchange', 'client'],
      url='https://github.com/peerchemist/dodo',
      author='Peerchemist',
      author_email='peerchemist@protonmail.ch',
      license='BSD',
      install_requires=['cryptotik', 'fire', 'keyring'],
      scripts=['bin/dodo']
      )
