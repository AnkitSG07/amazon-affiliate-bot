const products = [
    {
        title: "Amazon Brand - Presto! Garbage Bags | Medium | 180 Count | 30 Bags X 6 Rolls | 19 X 21 Inches | For Dry & Wet Waste | Black",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71T2M3bz77L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Amazon-Brand-Presto-Oxo-Biodegradable-Garbage/dp/B0821PN8L4/ref=zg_bs_c_kitchen_d_sccl_1/262-8249688-3890603?pd_rd_w=rNUks&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B0821PN8L4&psc=1&tag=ankit007"
    },
    {
        title: "Atom Weight Machine for Kitchen, Digital Scale with LCD Display, Scale for Home Baking, Cooking & Balance Diet. Weighing Machine with capacity 10Kg, 6 Months Warranty SF400/A121,Color May Vary",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71775fRr+gL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Weighing-Balanced-Batteries-Included-A121/dp/B083C6XMKQ/ref=zg_bs_c_kitchen_d_sccl_2/262-8249688-3890603?pd_rd_w=rNUks&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B083C6XMKQ&psc=1&tag=ankit007"
    },
    {
        title: "NutriPro Juicer Mixer Grinder - Smoothie Maker - 500 Watts (2 Jar, Silver) - 2 Year Warranty",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71PkRff5mdL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/NutriPro-Bullet-Juicer-Grinder-Blades/dp/B09J2T124D/ref=zg_bs_c_kitchen_d_sccl_3/262-8249688-3890603?pd_rd_w=rNUks&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B09J2T124D&psc=1&tag=ankit007"
    },
    {
        title: "Add2Cart Stainless Steel 11cm Tadka Pan, 400ml Capacity, for Spice Tempering/Seasoning, Induction Bottom and Gas Stove Ready, Long Wire Handle, Laser-Etched Scale, Smooth Finished Surface",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61pMrpkT1QL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Stainless-Tempering-Seasoning-Induction-Laser-Etched/dp/B0DBM8F5HY/ref=zg_bs_c_kitchen_d_sccl_4/262-8249688-3890603?pd_rd_w=rNUks&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B0DBM8F5HY&psc=1&tag=ankit007"
    },
    {
        title: "Ezee Black Garbage Bags for Dustbin | 90 Pcs | Medium 19 X 21 Inches | 30 Pcs x Pack of 3",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71erHCKJ3WL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Ezee-Garbage-Bag-inches-Pieces/dp/B06VX8YR6Q/ref=zg_bs_c_kitchen_d_sccl_5/262-8249688-3890603?pd_rd_w=rNUks&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B06VX8YR6Q&psc=1&tag=ankit007"
    },
    {
        title: "Zulaxy Photo Frame Hooks for Wall Without Drilling, 10 Pack Self Adhesive Hooks for Wall Heavy Duty Strong Nail Free for Hanging Photo Frame (Hanging Hook, Transparent) Stainless Steel",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61uaI9IfRUL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Zulaxy-Drilling-Adhesive-Transparent-Stainless/dp/B0CCM8L54V/ref=zg_bs_c_kitchen_d_sccl_6/262-8249688-3890603?pd_rd_w=rNUks&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B0CCM8L54V&psc=1&tag=ankit007"
    },
    {
        title: "Purepet Ocean Fish Adult Dry Cat Food, 1 kg",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61rrqJmufiL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Purepet-Ocean-Fish-Adult-Food/dp/B0BMGP89P1/ref=zg_bs_c_pet-supplies_d_sccl_1/262-8249688-3890603?pd_rd_w=M4SQl&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B0BMGP89P1&psc=1&tag=ankit007"
    },
    {
        title: "Meat Up Chicken Flavour Real Chicken Biscuit For All Life Stages Dog, 1kg (Buy 1 Get 1 Free)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/81ZwmefsZmL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Meatup-Chicken-Flavour-Biscuit-Treats/dp/B079T88XLM/ref=zg_bs_c_pet-supplies_d_sccl_2/262-8249688-3890603?pd_rd_w=M4SQl&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B079T88XLM&psc=1&tag=ankit007"
    },
    {
        title: "Pedigree Adult Dry Dog Food, Chicken & Vegetables, 3 kg, Contains 37 Essential Nutrients, 100% Complete & Balanced Food for Adult Dogs",
        image: "https://images-eu.ssl-images-amazon.com/images/I/81+YMZg8fAL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Pedigree-Adult-Food-Chicken-Vegetables/dp/B00LHS8I3A/ref=zg_bs_c_pet-supplies_d_sccl_3/262-8249688-3890603?pd_rd_w=M4SQl&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B00LHS8I3A&psc=1&tag=ankit007"
    },
    {
        title: "Pedigree Adult Wet Dog Food, Chicken & Liver Chunks in Gravy, 70 g (Pack of 30), Made with Real Meat, 100% Complete & Balanced Meal for Adult Dogs",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71rDGH-jUvL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Pedigree-Adult-Chicken-Liver-Chunks/dp/B084GNRLPW/ref=zg_bs_c_pet-supplies_d_sccl_4/262-8249688-3890603?pd_rd_w=M4SQl&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B084GNRLPW&psc=1&tag=ankit007"
    },
    {
        title: "Meat Up Dry Adult Dog Food, Chicken Flavour, 3 KG (Buy 1 Get 1 Free)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/716AueVULCL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Meat-Up-Adult-Food-Free/dp/B075WWBTYQ/ref=zg_bs_c_pet-supplies_d_sccl_5/262-8249688-3890603?pd_rd_w=M4SQl&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B075WWBTYQ&psc=1&tag=ankit007"
    },
    {
        title: "Drools Adult Dry Dog Food Chicken and Egg, 3kg with Free 1.2kg, Total 4.2 kg Pack",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71o84Bphv-L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Drools-Chicken-Adult-Food-Free/dp/B07HBMB3WW/ref=zg_bs_c_pet-supplies_d_sccl_6/262-8249688-3890603?pd_rd_w=M4SQl&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B07HBMB3WW&psc=1&tag=ankit007"
    },
    {
        title: "TEKCOOL 4000mAh Double Ended Spray Fan, Cold Air Fan, 2025 New 3 Gears USB Rechargeable Oscillating fan with LED Light Cooler Fan, Touch & Remote Control, 280ml Water Tank, Ice Filling Fan (White)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71dO8y8OU8L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/TEKCOOL-4000mAh-Rechargeable-Oscillating-fan/dp/B0DY51RDJT/ref=zg_bs_c_computers_d_sccl_1/262-8249688-3890603?pd_rd_w=w2sj3&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B0DY51RDJT&psc=1&tag=ankit007"
    },
    {
        title: "Ambrane Unbreakable 3A Fast Charging 1.5m Braided Type C Cable for Smartphones, Tablets & other Type C devices, 480Mbps Data Sync, Quick Charge 3.0 (RCT15A, Black)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61W8xeZTwxL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Ambrane-Unbreakable-Charging-Braided-Cable/dp/B098NS6PVG/ref=zg_bs_c_computers_d_sccl_2/262-8249688-3890603?pd_rd_w=w2sj3&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B098NS6PVG&psc=1&tag=ankit007"
    },
    {
        title: "Tukzer Tabletop Fully Foldable Desktop Tablet Mobile Stand Holder with Angle & Height Adjustable for Desk, Cradle, Dock, Compatible with Smartphones & Tablets (Black)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61CFLVpKrZL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Tukzer-Foldable-Adjustable-Compatible-Smartphones/dp/B08MWHHZDW/ref=zg_bs_c_computers_d_sccl_3/262-8249688-3890603?pd_rd_w=w2sj3&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B08MWHHZDW&psc=1&tag=ankit007"
    },
    {
        title: "Safari Omega Pro 35L Laptop Backpack with Raincover, 3 compartments, bottle holder, organizer, school bag for boys and girls, college bag for women and men, office bag, travel bag",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71maWXZscfL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Safari-Laptop-Backpack-Raincover-college/dp/B097JJ2CK6/ref=zg_bs_c_computers_d_sccl_4/262-8249688-3890603?pd_rd_w=w2sj3&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B097JJ2CK6&psc=1&tag=ankit007"
    },
    {
        title: "Logitech M186 Wireless Mouse, 2.4GHz with USB Mini Receiver, 12-Month Battery Life, 1000 DPI Optical Tracking, Ambidextrous, Compatible with PC, Mac, Laptop",
        image: "https://images-eu.ssl-images-amazon.com/images/I/41xAn0iwc6L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Logitech-Wireless-Receiver-Ambidextrous-Compatible/dp/B0D18192T2/ref=zg_bs_c_computers_d_sccl_5/262-8249688-3890603?pd_rd_w=w2sj3&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B0D18192T2&psc=1&tag=ankit007"
    },
    {
        title: "AmazonBasics Port L15 Carry Case Bag",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61wrI74wR1L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Amazonbasics-Port-L15-Carry-Case/dp/B0C8NY5LVQ/ref=zg_bs_c_computers_d_sccl_6/262-8249688-3890603?pd_rd_w=w2sj3&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B0C8NY5LVQ&psc=1&tag=ankit007"
    },
    {
        title: "(Refurbished) Nokia All-New 105 Dual Sim Keypad Phone with Built-in UPI Payments, Long-Lasting Battery, Wireless FM Radio | Cyan",
        image: "https://images-eu.ssl-images-amazon.com/images/I/614lMzqevmL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Refurbished-Nokia-105-Payments-Long-Lasting/dp/B0CF2M9QVY/ref=zg_bs_c_amazon-renewed_d_sccl_1/262-8249688-3890603?pd_rd_w=KdaPg&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B0CF2M9QVY&psc=1&tag=ankit007"
    },
    {
        title: "(Refurbished) Lenovo ThinkPad 6th Gen Intel Core i5 Thin & Light HD Laptop (16GB RAM / 512GB SSD /14" (35.6 cm) HD/Windows 11/MS Office/WiFi/Webcam/Intel Graphics), Black",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61vGumezioL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Refurbished-Lenovo-ThinkPad-Windows-Graphics/dp/B0CR496TBN/ref=zg_bs_c_amazon-renewed_d_sccl_2/262-8249688-3890603?pd_rd_w=KdaPg&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B0CR496TBN&psc=1&tag=ankit007"
    },
    {
        title: "(Refurbished) Boya BYM1 Omnidirectional Lavalier Condenser Microphone with 20ft Audio Cable (Black)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61zICp6Ns0L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Boya-Omnidirectional-Lavalier-Condenser-Microphone/dp/B07QWDTND8/ref=zg_bs_c_amazon-renewed_d_sccl_3/262-8249688-3890603?pd_rd_w=KdaPg&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B07QWDTND8&psc=1&tag=ankit007"
    },
    {
        title: "(Refurbished) Lenovo ThinkPad 8th Gen Intel Core i5 Thin & Light HD Laptop (16 GB DDR4 RAM/512 GB SSD/14 (35.6 cm) HD/Windows 11/MS Office/WiFi/Bluetooth 4.1/Webcam/Intel Graphics)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/611AaVzaCQL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Refurbished-Lenovo-ThinkPad-Bluetooth-Graphics/dp/B0DMTPY8PJ/ref=zg_bs_c_amazon-renewed_d_sccl_4/262-8249688-3890603?pd_rd_w=KdaPg&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B0DMTPY8PJ&psc=1&tag=ankit007"
    },
    {
        title: "(Refurbished) Nokia All-New 105 Keypad Phone with Built-in UPI Payments, Long-Lasting Battery, Wireless FM Radio | Charcoal",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61DCQ4hgM5L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Refurbished-Nokia-105-Payments-Long-Lasting/dp/B0C7ZP9LJC/ref=zg_bs_c_amazon-renewed_d_sccl_5/262-8249688-3890603?pd_rd_w=KdaPg&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B0C7ZP9LJC&psc=1&tag=ankit007"
    },
    {
        title: "(Renewed) MI Xiaomi Wireless Home Security Camera 2i 2022 Edition | Full HD Picture | 360° View | 2MP | AI Powered Motion Detection | Enhanced Night Vision| Talk Back Feature (2 Way Calling), White",
        image: "https://images-eu.ssl-images-amazon.com/images/I/51Rvl7DuOUL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/MI-Wireless-Security-Detection-Enhanced/dp/B0BCG9N82J/ref=zg_bs_c_amazon-renewed_d_sccl_6/262-8249688-3890603?pd_rd_w=KdaPg&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B0BCG9N82J&psc=1&tag=ankit007"
    },
    {
        title: "Ghar Soaps Sandalwood & Saffron Magic Soaps For Bath (300 Gms Pack Of 3) | Paraben Free | Chandan & Kesar Bath Soap | Handmade Soaps For Glowing | Skin Brightening Soap For Men & Women",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71A7tvxJXPL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Sandalwood-Saffron-300-Handmade-Whitening/dp/B09S6M7JQJ/ref=zg_bs_c_beauty_d_sccl_1/262-8249688-3890603?pd_rd_w=HZhby&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B09S6M7JQJ&psc=1&tag=ankit007"
    },
    {
        title: "The Derma Co 1% Hyaluronic Sunscreen Aqua Gel SPF 50 PA++++ I For Oily, Dry, Acne-prone Skin | Ultra Lightweight Texture I Non-Greasy, No White Cast | Broad Spectrum Protection & Blue Light Protection | For Men & Women | 80 g",
        image: "https://images-eu.ssl-images-amazon.com/images/I/51dtLecU5QL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Derma-Co-Hyaluronic-Lightweight-white-cast/dp/B0BVWDJTHF/ref=zg_bs_c_beauty_d_sccl_2/262-8249688-3890603?pd_rd_w=HZhby&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B0BVWDJTHF&psc=1&tag=ankit007"
    },
    {
        title: "Cetaphil Paraben, Sulphate-Free Gentle Skin Hydrating Face Wash Cleanser with Niacinamide, Vitamin B5 for Dry to Normal, Sensitive Skin - 125 ml",
        image: "https://images-eu.ssl-images-amazon.com/images/I/51O+J5jnXcL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Cetaphil-Sulphate-Free-Hydrating-Niacinamide-Sensitive/dp/B01CCGW4OE/ref=zg_bs_c_beauty_d_sccl_3/262-8249688-3890603?pd_rd_w=HZhby&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B01CCGW4OE&psc=1&tag=ankit007"
    },
    {
        title: "Simple Kind To Skin Refreshing Face Wash 150 ml | 100% soap-free gentle cleanser for sensitive, dry & oily skin, for women & men",
        image: "https://images-eu.ssl-images-amazon.com/images/I/51lV2Pem64L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Simple-Kind-Refreshing-Facial-Globalbeauty/dp/B000LQUA6M/ref=zg_bs_c_beauty_d_sccl_4/262-8249688-3890603?pd_rd_w=HZhby&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B000LQUA6M&psc=1&tag=ankit007"
    },
    {
        title: "DOT & KEY Vitamin C + E Super Bright Sunscreen Spf 50 |Water-Light,UVA/UVB & Blue Light Protection|For Even Toned & Glowing Skin|With Liquid Spf 50+++| No White Cast| For All Skin Types| 50G,Pack Of 1",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61UGAajCkwL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Vitamin-Sunscreen-Water-Light-Protection-Absorption/dp/B0BLK4YRSN/ref=zg_bs_c_beauty_d_sccl_5/262-8249688-3890603?pd_rd_w=HZhby&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B0BLK4YRSN&psc=1&tag=ankit007"
    },
    {
        title: "Be Bodywise 4% Aha Bha Underarm Roll On 50ml | 2% Lactic Acid, 1% Mandelic Acid, 1% Salicylic Acid | Controls Odour & Reduces Pigmentation | 0% Alcohol & 0% Aluminium | Flora Fragrance",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71waYmGy3EL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Be-Bodywise-Salicylic-Pigmentation-Fragrance/dp/B0BRJWZNVM/ref=zg_bs_c_beauty_d_sccl_6/262-8249688-3890603?pd_rd_w=HZhby&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B0BRJWZNVM&psc=1&tag=ankit007"
    },
    {
        title: "HIT Flying Insect Killer - Mosquito & Fly Killer Spray (400ml) | Instant Kill | Protection from Dengue & Malaria",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61H-2CyQa2L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/HIT-Spray-Dengue-Malaria-Killer/dp/B00WK1DONW/ref=zg_bs_c_garden_d_sccl_1/262-8249688-3890603?pd_rd_w=Zaobm&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B00WK1DONW&psc=1&tag=ankit007"
    },
    {
        title: "Classic Mosquito Net for Double Bed | King Size Foldable Machardani | Polyester 30GSM Strong Net | PVC Coated Corrosion Resistant Steel Wire - Blue",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61IOb4Nu6AL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Classic-Mosquito-Net-Foldable-Saviours/dp/B00JD8EA1U/ref=zg_bs_c_garden_d_sccl_2/262-8249688-3890603?pd_rd_w=Zaobm&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B00JD8EA1U&psc=1&tag=ankit007"
    },
    {
        title: "HIT Crawling Insect Killer Cockroach Killer Spray | Instant Kill | Deep-Reach Nozzle | Fresh Fragrance, 700ml",
        image: "https://images-eu.ssl-images-amazon.com/images/I/612O8HhPFJL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/HIT-Cockroach-Killer-Spray-700ml/dp/B07WQJLYQM/ref=zg_bs_c_garden_d_sccl_3/262-8249688-3890603?pd_rd_w=Zaobm&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B07WQJLYQM&psc=1&tag=ankit007"
    },
    {
        title: "HIT Anti Mosquito Racquet | 6 months Warranty | Rechargeable Mosquito Killer Bat with LED Light | Charge Before Use",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71Xe3zMVWeL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/HIT-Anti-Mosquito-Racquet-Rechargeable/dp/B07S5FBY3J/ref=zg_bs_c_garden_d_sccl_4/262-8249688-3890603?pd_rd_w=Zaobm&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B07S5FBY3J&psc=1&tag=ankit007"
    },
    {
        title: "Weird Wolf 2 in 1 UV Light Electric Fly Swatter Mosquito Racket Bat with Base Stand, Lithium Battery, USB Charging, 6 Months Warranty, Green",
        image: "https://images-eu.ssl-images-amazon.com/images/I/81+Z+yZs8RL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Mosquito-Lithium-Battery-Charging-Warranty/dp/B0C3XV4CGJ/ref=zg_bs_c_garden_d_sccl_5/262-8249688-3890603?pd_rd_w=Zaobm&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B0C3XV4CGJ&psc=1&tag=ankit007"
    },
    {
        title: "Amazon Brand - All Season Lotus Flower 20 Seeds/Pack, Japanese Rain bow Lotus Flower Seeds, Dwarf Rainbow Flower Seed, Rainbow Lotus Flower Seeds for Home Decor Kamal Gatta Seed, Home Gardening",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71ba46ZQFVL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Amazon-Brand-Japanese-Rainbow-Gardening/dp/B0F12TN786/ref=zg_bs_c_garden_d_sccl_6/262-8249688-3890603?pd_rd_w=Zaobm&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=YF0B01EV11CVS0C5XSH0&pd_rd_wg=AMMtA&pd_rd_r=6fb5fbc0-9210-4ecc-92bd-2db672f36bbe&pd_rd_i=B0F12TN786&psc=1&tag=ankit007"
    },
];
