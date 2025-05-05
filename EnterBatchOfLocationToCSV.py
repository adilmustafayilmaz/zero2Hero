import csv
import os

def main():
    # Create a list to store the input data
    data = []
    
    print("Enter links one by one. Type 'exit' to finish and save to CSV.")
    print("Format: [Location name] [Link]")
    print("Example: Central Park https://example.com/central-park")
    
    while True:
        user_input = input("\nEnter location and link (or 'exit' to quit): ")
        
        # Exit condition
        if user_input.lower() == 'exit':
            break
        
        # Parse input to extract location and link
        try:
            # Find the first occurrence of http or https
            parts = user_input.split()
            link_index = next((i for i, part in enumerate(parts) if part.startswith('http')), -1)
            
            if link_index == -1:
                print("Error: No valid link found. Make sure your link starts with http:// or https://")
                continue
            
            # Everything before the link is the location name
            location = ' '.join(parts[:link_index])
            link = ' '.join(parts[link_index:])
            
            # Add to data list
            data.append([location, link])
            print(f"Added: Location = '{location}', Link = '{link}'")
            
        except Exception as e:
            print(f"Error processing input: {e}")
            print("Please try again with the format: [Location name] [Link]")
    
    # Save data to CSV if we have any entries
    if data:
        # Define CSV filename
        csv_filename = "location_links_collection.csv"
        
        # Check if file exists to determine if we need to write headers
        file_exists = os.path.isfile(csv_filename)
        
        # Open CSV file and write data
        with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Write header only if the file is new
            if not file_exists:
                writer.writerow(["Location", "Link"])
            
            # Write all the data rows
            writer.writerows(data)
        
        print(f"\nSaved {len(data)} entries to {csv_filename}")
    else:
        print("\nNo data to save.")

if __name__ == "__main__":
    main()