def get_party_recommendations(budget_input: PartyBudgetInput) -> dict:
    """Generate party planning recommendations within budget in INR for Indian market"""
    try:
        prompt = f"""
        I need party planning recommendations for India with a total budget of ₹{budget_input.total_budget:.2f}.

        Party details:
        - Type: {budget_input.party_type}
        - Number of guests: {budget_input.num_guests}
        - Venue type: {budget_input.venue_type or "Not specified"}
        - Catering needed: {"Yes" if budget_input.needs_catering else "No"}
        - Decoration needed: {"Yes" if budget_input.needs_decoration else "No"}
        - Entertainment needed: {"Yes" if budget_input.needs_entertainment else "No"}

        Additional requirements: {budget_input.additional_requirements or "None"}

        Please provide a detailed budget breakdown with specific recommendations
        available in India using INR prices. Use Indian brands, vendors, and typical
        cost expectations.

        Format your response as JSON with the following structure:

        {
            "total_budget": {budget_input.total_budget:.2f},
            "budget_breakdown": [
                {
                    "category": "venue",
                    "allocation": 0.0,
                    "items": [
                        {
                            "name": "",
                            "description": "",
                            "estimated_price": 0.0,
                            "quantity": 0,
                            "search_terms": ""
                        }
                    ]
                }
            ],
            "venue_suggestions": [
                {
                    "name": "",
                    "type": "",
                    "capacity": 0,
                    "estimated_cost": 0.0,
                    "search_terms": ""
                }
            ],
            "remaining_budget": 0.0,
            "additional_suggestions": []
        }

        Ensure all costs are in INR and total does not exceed the given budget.
        Provide search terms suitable for Indian websites such as BookMyShow,
        Swiggy, Flipkart, etc.
        """

        response = model.generate_content(prompt)
        result = extract_json_from_response(response.text)

        # Create INR calculation table
        result["calculation_table"] = []
        categories = {}

        for category in result.get("budget_breakdown", []):
            cat_name = category.get("category", "Misc")
            cat_allocation = category.get("allocation", 0)

            if cat_name not in categories:
                categories[cat_name] = {
                    "category": cat_name,
                    "items_count": 0,
                    "total_cost": 0,
                    "percentage_of_budget": 0
                }

            for item in category.get("items", []):
                categories[cat_name]["items_count"] += 1
                categories[cat_name]["total_cost"] += item.get(
                    "estimated_price", 0
                )

            if result["total_budget"] > 0:
                categories[cat_name]["percentage_of_budget"] = (
                    categories[cat_name]["total_cost"]
                    / result["total_budget"]
                ) * 100

        for cat_data in categories.values():
            result["calculation_table"].append(cat_data)

        # Define relevant shopping platforms for each category
        category_platforms = {
            "venue": ["booking", "makemytrip", "yoyrooms", "nobroker"],
            "catering": ["swiggy", "zomato"],
            "decoration": ["amazon", "flipkart", "meesho", "blinkit"],
            "drinks": ["swiggy", "zomato", "bigbasket", "flipkart"],
            "entertainment": ["bookmyshow", "amazon", "flipkart"],
            "gifts": ["amazon", "flipkart", "nykaa", "meesho"],
            "photography": ["rooftop", "snapdeal", "nearby"],
            "music": ["amazon", "flipkart", "bookmyshow"],
            "accessories": ["amazon", "flipkart", "nykaa", "meesho"],
            "transportation": ["makemytrip", "goibibo", "uber"],
            "travel": ["makemytrip", "flipkart", "booking"],
        }

        # Default platforms if category is not in our predefined list
        default_platforms = ["amazon", "flipkart", "google"]

        # Add shopping links for each item
        for category in result.get("budget_breakdown", []):
            cat_name = category.get("category", "").lower()
            relevant_platforms = category_platforms.get(
                cat_name, default_platforms
            )

            for item in category.get("items", []):
                search_terms = item.get("search_terms", "")

                if search_terms:
                    item["shopping_links"] = {}

                    if "amazon" in relevant_platforms:
                        item["shopping_links"]["amazon"] = (
                            f"https://www.amazon.in/s?k={quote_plus(search_terms)}"
                        )

                    if "flipkart" in relevant_platforms:
                        item["shopping_links"]["flipkart"] = (
                            f"https://www.flipkart.com/search?q={quote_plus(search_terms)}"
                        )

                    if "meesho" in relevant_platforms:
                        item["shopping_links"]["meesho"] = (
                            f"https://www.meesho.com/search?q={quote_plus(search_terms)}"
                        )

                    if "nykaa" in relevant_platforms:
                        item["shopping_links"]["nykaa"] = (
                            f"https://www.nykaa.com/search/result/?q={quote_plus(search_terms)}"
                        )

        # Add venue links
        venue_platforms = [
            "google",
            "bookmyshow",
            "makemytrip",
            "yoyrooms",
            "nobroker"
        ]

        for venue in result.get("venue_suggestions", []):
            search_terms = venue.get("search_terms", "")

            if search_terms:
                venue["search_links"] = {}

                if "google" in venue_platforms:
                    venue["search_links"]["google"] = (
                        f"https://www.google.com/search?q={quote_plus(search_terms)}"
                    )

                if "bookmyshow" in venue_platforms:
                    venue["search_links"]["bookmyshow"] = (
                        f"https://in.bookmyshow.com/search/?q={quote_plus(search_terms)}"
                    )

                if "makemytrip" in venue_platforms:
                    venue["search_links"]["makemytrip"] = (
                        f"https://www.makemytrip.com/hotels/hotel-listing/?searchText={quote_plus(search_terms)}"
                    )

                if "yoyrooms" in venue_platforms:
                    venue["search_links"]["yoyrooms"] = (
                        f"https://www.yoyrooms.com/search?q={quote_plus(search_terms)}"
                    )

                if "nobroker" in venue_platforms:
                    venue["search_links"]["nobroker"] = (
                        f"https://www.nobroker.in/property/search?query={quote_plus(search_terms)}"
                    )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )