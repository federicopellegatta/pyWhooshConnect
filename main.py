from src import __title__, __version__, __description__

def main():
    width: int = 50

    print("="*width)
    print(f"{__title__} v{__version__}".center(width))
    print(f"{__description__}".center(width))
    print("="*width)
    print("\n✓ Application started successfully!")


if __name__ == '__main__':
    main()