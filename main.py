# main.py

from asg_updater import ASGUpdater

def main():
    print("\n=== Auto Scaling Group Update Tool ===")
    try:
        updater = ASGUpdater()
        
        # You can either use default values from config.py
        updater.apply_new_configuration()
        
        # Or provide specific values
        # updater.apply_new_configuration(
        #     new_image_id="your-new-image-id",
        #     template_version="v2"
        # )
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()