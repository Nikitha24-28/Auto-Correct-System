def main():
    """Main function."""
    print_banner()
    
    # Initialize system
    print(f"{Fore.YELLOW}Initializing autocomplete system...")
    system = AutocompleteSystem(cache_size=1000, enable_spell_check=True)

    print(f"\n{Fore.CYAN}{'═' * 60}")
    print(f"{Fore.YELLOW}Dictionary Loading Options:")
    print(f"{Fore.WHITE}  1. Load sample dictionary (built-in)")
    print(f"{Fore.WHITE}  2. Load from file (data/dictionary.txt)")
    print(f"{Fore.WHITE}  3. Download from API (10,000+ words)")
    print(f"{Fore.CYAN}{'═' * 60}")
    
    choice = input(f"{Fore.CYAN}Select option (1-3, or press Enter for default): {Style.RESET_ALL}").strip()
    
    if choice == '3':
        # Load from API
        word_count = system.load_from_api(limit=10000)
        print(f"{Fore.GREEN}✓ Loaded {word_count} words\n")
    elif choice == '2':
        # Load from file
        dict_file = "data/dictionary.txt"
        if os.path.exists(dict_file):
            word_count = system.load_dictionary(dict_file)
            print(f"{Fore.GREEN}✓ Loaded {word_count} words\n")
        else:
            print(f"{Fore.RED}File not found: {dict_file}")
            print(f"{Fore.YELLOW}Loading sample dictionary instead...")
            word_count = load_sample_dictionary(system)
            print(f"{Fore.GREEN}✓ Loaded {word_count} words\n")
    else:
        # Default: Load sample dictionary
        print(f"{Fore.YELLOW}Loading sample dictionary...")
        word_count = load_sample_dictionary(system)
        print(f"{Fore.GREEN}✓ Loaded {word_count} words\n")
    
    # Show menu
    while True:
        print(f"{Fore.CYAN}{'═' * 60}")
        print(f"{Fore.YELLOW}Select mode:")
        print(f"{Fore.WHITE}  1. Interactive search")
        print(f"{Fore.WHITE}  2. Performance benchmark")
        print(f"{Fore.WHITE}  3. View statistics")
        print(f"{Fore.WHITE}  4. Exit")
        print(f"{Fore.CYAN}{'═' * 60}")
        
        choice = input(f"{Fore.CYAN}Enter choice (1-4): {Style.RESET_ALL}").strip()
        
        if choice == '1':
            interactive_mode(system)
        elif choice == '2':
            benchmark_mode(system)
        elif choice == '3':
            print_statistics(system)
        elif choice == '4':
            print(f"{Fore.YELLOW}Thank you for using Autocomplete System!")
            break
        else:
            print(f"{Fore.RED}Invalid choice. Please try again.\n")