# main.py

from asg_updater import ASGUpdater

def main():
    print("\n=== Auto Scaling Group Update Tool ===")
    try:
        updater = ASGUpdater()
        

        updater.apply_new_configuration()
        
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()