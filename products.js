const products = [
    {
        title: "pTron Newly Launched Fusion Tunes 10W Mini Bluetooth Speaker with Wireless Karaoke Mic, 8Hrs Playtime, Vivid RGB Lights, Voice Effects, Multi-Play Modes BT5.1/TF Card & Type-C Charging Port (Black)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61Lgfcc+o-L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/pTron-Launched-Fusion-Bluetooth-Multi-Play/dp/B0D772K8X8/ref=zg_bs_c_musical-instruments_d_sccl_1/259-6819556-7907717?pd_rd_w=KkJ6O&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B0D772K8X8&psc=1&tag=ankit007"
    },
    {
        title: "GRENARO Mic for YouTube Wireless, 3-Level Adjustable Noise Reduction Mic Wireless, Wireless Microphone for Youtubers with LED Indicator Light (Single Channel Type-C Port Version)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71qNXTJgktL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/GRENARO-Single-Channel-Type-C-Version/dp/B0DQD8HWWG/ref=zg_bs_c_musical-instruments_d_sccl_2/259-6819556-7907717?pd_rd_w=KkJ6O&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B0DQD8HWWG&psc=1&tag=ankit007"
    },
    {
        title: "Juârez JRZ250 One Handed Trigger Guitar Metal Capo Quick Change for Ukulele, Electric and Acoustic Guitars, Black",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71rEeRq9oyL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Juarez-Trigger-Ukulele-Electric-Acoustic/dp/B072FH5KLJ/ref=zg_bs_c_musical-instruments_d_sccl_3/259-6819556-7907717?pd_rd_w=KkJ6O&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B072FH5KLJ&psc=1&tag=ankit007"
    },
    {
        title: "Radhe Flutes | Right Handed C Natural With Velvet Cover | Tuned With Tanpura A=440Hz | PVC Fiber",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61gkHwcc5HL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Radhe-Flutes-Natural-Bansuri-Middle/dp/B07T35ZBHB/ref=zg_bs_c_musical-instruments_d_sccl_4/259-6819556-7907717?pd_rd_w=KkJ6O&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B07T35ZBHB&psc=1&tag=ankit007"
    },
    {
        title: "Boya ByM1 Auxiliary Omnidirectional Lavalier Condenser Microphone with 20ft Audio Cable (Black)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/51MHP1XXmWL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Boya-Omnidirectional-Lavalier-Condenser-Microphone/dp/B076B8G5D8/ref=zg_bs_c_musical-instruments_d_sccl_5/259-6819556-7907717?pd_rd_w=KkJ6O&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B076B8G5D8&psc=1&tag=ankit007"
    },
    {
        title: "Juârez Acoustic Guitar Kit, 38 Inch Cutaway, 038C with Bag, Strings, Pick and Strap, Black",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71y1TJbygLL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Juarez-Acoustic-Cutaway-038C-Strings/dp/B017NPCSLI/ref=zg_bs_c_musical-instruments_d_sccl_6/259-6819556-7907717?pd_rd_w=KkJ6O&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B017NPCSLI&psc=1&tag=ankit007"
    },
    {
        title: "Add2Cart Stainless Steel 11cm Tadka Pan, 400ml Capacity, for Spice Tempering/Seasoning, Induction Bottom and Gas Stove Ready, Long Wire Handle, Laser-Etched Scale, Smooth Finished Surface",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61pMrpkT1QL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Stainless-Tempering-Seasoning-Induction-Laser-Etched/dp/B0DBM8F5HY/ref=zg_bs_c_kitchen_d_sccl_1/259-6819556-7907717?pd_rd_w=a0D98&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B0DBM8F5HY&psc=1&tag=ankit007"
    },
    {
        title: "Amazon Brand - Presto! Garbage Bags | Medium | 180 Count | 30 Bags X 6 Rolls | 19 X 21 Inches | For Dry & Wet Waste | Black",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71T2M3bz77L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Amazon-Brand-Presto-Oxo-Biodegradable-Garbage/dp/B0821PN8L4/ref=zg_bs_c_kitchen_d_sccl_2/259-6819556-7907717?pd_rd_w=a0D98&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B0821PN8L4&psc=1&tag=ankit007"
    },
    {
        title: "Atom Weight Machine for Kitchen, Digital Scale with LCD Display, Scale for Home Baking, Cooking & Balance Diet. Weighing Machine with capacity 10Kg, 6 Months Warranty SF400/A121,Color May Vary",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71775fRr+gL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Weighing-Balanced-Batteries-Included-A121/dp/B083C6XMKQ/ref=zg_bs_c_kitchen_d_sccl_3/259-6819556-7907717?pd_rd_w=a0D98&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B083C6XMKQ&psc=1&tag=ankit007"
    },
    {
        title: "NutriPro Juicer Mixer Grinder - Smoothie Maker - 500 Watts (2 Jar, Silver) - 2 Year Warranty",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71PkRff5mdL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/NutriPro-Bullet-Juicer-Grinder-Blades/dp/B09J2T124D/ref=zg_bs_c_kitchen_d_sccl_4/259-6819556-7907717?pd_rd_w=a0D98&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B09J2T124D&psc=1&tag=ankit007"
    },
    {
        title: "Ezee Black Garbage Bags for Dustbin | 90 Pcs | Medium 19 X 21 Inches | 30 Pcs x Pack of 3",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71erHCKJ3WL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Ezee-Garbage-Bag-inches-Pieces/dp/B06VX8YR6Q/ref=zg_bs_c_kitchen_d_sccl_5/259-6819556-7907717?pd_rd_w=a0D98&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B06VX8YR6Q&psc=1&tag=ankit007"
    },
    {
        title: "Zulaxy Photo Frame Hooks for Wall Without Drilling, 10 Pack Self Adhesive Hooks for Wall Heavy Duty Strong Nail Free for Hanging Photo Frame (Hanging Hook, Transparent) Stainless Steel",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61uaI9IfRUL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Zulaxy-Drilling-Adhesive-Transparent-Stainless/dp/B0CCM8L54V/ref=zg_bs_c_kitchen_d_sccl_6/259-6819556-7907717?pd_rd_w=a0D98&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B0CCM8L54V&psc=1&tag=ankit007"
    },
    {
        title: "Purepet Ocean Fish Adult Dry Cat Food, 1 kg",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61rrqJmufiL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Purepet-Ocean-Fish-Adult-Food/dp/B0BMGP89P1/ref=zg_bs_c_pet-supplies_d_sccl_1/259-6819556-7907717?pd_rd_w=cRkou&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B0BMGP89P1&psc=1&tag=ankit007"
    },
    {
        title: "Meat Up Chicken Flavour Real Chicken Biscuit For All Life Stages Dog, 1kg (Buy 1 Get 1 Free)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/81ZwmefsZmL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Meatup-Chicken-Flavour-Biscuit-Treats/dp/B079T88XLM/ref=zg_bs_c_pet-supplies_d_sccl_2/259-6819556-7907717?pd_rd_w=cRkou&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B079T88XLM&psc=1&tag=ankit007"
    },
    {
        title: "Pedigree Adult Wet Dog Food, Chicken & Liver Chunks in Gravy, 70 g (Pack of 30), Made with Real Meat, 100% Complete & Balanced Meal for Adult Dogs",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71rDGH-jUvL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Pedigree-Adult-Chicken-Liver-Chunks/dp/B084GNRLPW/ref=zg_bs_c_pet-supplies_d_sccl_3/259-6819556-7907717?pd_rd_w=cRkou&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B084GNRLPW&psc=1&tag=ankit007"
    },
    {
        title: "Pedigree Adult Dry Dog Food, Chicken & Vegetables, 3 kg, Contains 37 Essential Nutrients, 100% Complete & Balanced Food for Adult Dogs",
        image: "https://images-eu.ssl-images-amazon.com/images/I/81+YMZg8fAL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Pedigree-Adult-Food-Chicken-Vegetables/dp/B00LHS8I3A/ref=zg_bs_c_pet-supplies_d_sccl_4/259-6819556-7907717?pd_rd_w=cRkou&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B00LHS8I3A&psc=1&tag=ankit007"
    },
    {
        title: "Meat Up Dry Adult Dog Food, Chicken Flavour, 3 KG (Buy 1 Get 1 Free)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/716AueVULCL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Meat-Up-Adult-Food-Free/dp/B075WWBTYQ/ref=zg_bs_c_pet-supplies_d_sccl_5/259-6819556-7907717?pd_rd_w=cRkou&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B075WWBTYQ&psc=1&tag=ankit007"
    },
    {
        title: "Drools Adult Dry Dog Food Chicken and Egg, 3kg with Free 1.2kg, Total 4.2 kg Pack",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71o84Bphv-L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Drools-Chicken-Adult-Food-Free/dp/B07HBMB3WW/ref=zg_bs_c_pet-supplies_d_sccl_6/259-6819556-7907717?pd_rd_w=cRkou&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B07HBMB3WW&psc=1&tag=ankit007"
    },
    {
        title: "TEKCOOL 4000mAh Double Ended Spray Fan, Cold Air Fan, 2025 New 3 Gears USB Rechargeable Oscillating fan with LED Light Cooler Fan, Touch & Remote Control, 280ml Water Tank, Ice Filling Fan (White)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71dO8y8OU8L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/TEKCOOL-4000mAh-Rechargeable-Oscillating-fan/dp/B0DY51RDJT/ref=zg_bs_c_computers_d_sccl_1/259-6819556-7907717?pd_rd_w=CQfuC&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B0DY51RDJT&psc=1&tag=ankit007"
    },
    {
        title: "Ambrane Unbreakable 3A Fast Charging 1.5m Braided Type C Cable for Smartphones, Tablets & other Type C devices, 480Mbps Data Sync, Quick Charge 3.0 (RCT15A, Black)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61W8xeZTwxL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Ambrane-Unbreakable-Charging-Braided-Cable/dp/B098NS6PVG/ref=zg_bs_c_computers_d_sccl_2/259-6819556-7907717?pd_rd_w=CQfuC&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B098NS6PVG&psc=1&tag=ankit007"
    },
    {
        title: "Safari Omega Pro 35L Laptop Backpack with Raincover, 3 compartments, bottle holder, organizer, school bag for boys and girls, college bag for women and men, office bag, travel bag",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71maWXZscfL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Safari-Laptop-Backpack-Raincover-college/dp/B097JJ2CK6/ref=zg_bs_c_computers_d_sccl_3/259-6819556-7907717?pd_rd_w=CQfuC&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B097JJ2CK6&psc=1&tag=ankit007"
    },
    {
        title: "Logitech M186 Wireless Mouse, 2.4GHz with USB Mini Receiver, 12-Month Battery Life, 1000 DPI Optical Tracking, Ambidextrous, Compatible with PC, Mac, Laptop",
        image: "https://images-eu.ssl-images-amazon.com/images/I/41xAn0iwc6L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Logitech-Wireless-Receiver-Ambidextrous-Compatible/dp/B0D18192T2/ref=zg_bs_c_computers_d_sccl_4/259-6819556-7907717?pd_rd_w=CQfuC&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B0D18192T2&psc=1&tag=ankit007"
    },
    {
        title: "Dell MS116 Wired Optical Mouse, 1000DPI, LED Tracking, Scrolling Wheel, Plug and Play",
        image: "https://images-eu.ssl-images-amazon.com/images/I/51a1LryFTZS._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Dell-MS116-1000DPI-Wired-Optical/dp/B01HJI0FS2/ref=zg_bs_c_computers_d_sccl_5/259-6819556-7907717?pd_rd_w=CQfuC&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B01HJI0FS2&psc=1&tag=ankit007"
    },
    {
        title: "STRIFF Adjustable Laptop Tabletop Stand Patented Riser Ventilated Portable Foldable Compatible with MacBook Notebook Tablet Tray Desk Table Book with Free Phone Stand (Black)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71Zf9uUp+GL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/STRIFF-Adjustable-Patented-Ventilated-Compatible/dp/B07XCM6T4N/ref=zg_bs_c_computers_d_sccl_6/259-6819556-7907717?pd_rd_w=CQfuC&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B07XCM6T4N&psc=1&tag=ankit007"
    },
    {
        title: "(Refurbished) Nokia All-New 105 Dual Sim Keypad Phone with Built-in UPI Payments, Long-Lasting Battery, Wireless FM Radio | Cyan",
        image: "https://images-eu.ssl-images-amazon.com/images/I/614lMzqevmL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Refurbished-Nokia-105-Payments-Long-Lasting/dp/B0CF2M9QVY/ref=zg_bs_c_amazon-renewed_d_sccl_1/259-6819556-7907717?pd_rd_w=X0nSA&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B0CF2M9QVY&psc=1&tag=ankit007"
    },
    {
        title: "(Refurbished) Boya BYM1 Omnidirectional Lavalier Condenser Microphone with 20ft Audio Cable (Black)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61zICp6Ns0L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Boya-Omnidirectional-Lavalier-Condenser-Microphone/dp/B07QWDTND8/ref=zg_bs_c_amazon-renewed_d_sccl_2/259-6819556-7907717?pd_rd_w=X0nSA&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B07QWDTND8&psc=1&tag=ankit007"
    },
    {
        title: "(Refurbished) Lenovo ThinkPad 6th Gen Intel Core i5 Thin & Light HD Laptop (16GB RAM / 512GB SSD /14" (35.6 cm) HD/Windows 11/MS Office/WiFi/Webcam/Intel Graphics), Black",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61vGumezioL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Refurbished-Lenovo-ThinkPad-Windows-Graphics/dp/B0CR496TBN/ref=zg_bs_c_amazon-renewed_d_sccl_3/259-6819556-7907717?pd_rd_w=X0nSA&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B0CR496TBN&psc=1&tag=ankit007"
    },
    {
        title: "(Refurbished) Lenovo ThinkPad 8th Gen Intel Core i5 Thin & Light HD Laptop (16 GB DDR4 RAM/512 GB SSD/14 (35.6 cm) HD/Windows 11/MS Office/WiFi/Bluetooth 4.1/Webcam/Intel Graphics)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/611AaVzaCQL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Refurbished-Lenovo-ThinkPad-Bluetooth-Graphics/dp/B0DMTPY8PJ/ref=zg_bs_c_amazon-renewed_d_sccl_4/259-6819556-7907717?pd_rd_w=X0nSA&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B0DMTPY8PJ&psc=1&tag=ankit007"
    },
    {
        title: "(Refurbished) Nokia All-New 105 Keypad Phone with Built-in UPI Payments, Long-Lasting Battery, Wireless FM Radio | Charcoal",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61DCQ4hgM5L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Refurbished-Nokia-105-Payments-Long-Lasting/dp/B0C7ZP9LJC/ref=zg_bs_c_amazon-renewed_d_sccl_5/259-6819556-7907717?pd_rd_w=X0nSA&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B0C7ZP9LJC&psc=1&tag=ankit007"
    },
    {
        title: "(Refurbished) iQOO Z7 Pro 5G (Blue Lagoon, 8GB RAM, 256GB Storage) | 3D Curved AMOLED Display | 4nm MediaTek Dimesity 7200 5G Processor | 64MP Aura Light OIS Camera | Segment's Slimmest & Lightest Smartphone",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61Id6WJDWqL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Refurbished-iQOO-MediaTek-Processor-Smartphone/dp/B0CV5NDGB5/ref=zg_bs_c_amazon-renewed_d_sccl_6/259-6819556-7907717?pd_rd_w=X0nSA&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B0CV5NDGB5&psc=1&tag=ankit007"
    },
    {
        title: "Ghar Soaps Sandalwood & Saffron Magic Soaps For Bath (300 Gms Pack Of 3) | Paraben Free | Chandan & Kesar Bath Soap | Handmade Soaps For Glowing | Skin Brightening Soap For Men & Women",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71A7tvxJXPL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Sandalwood-Saffron-300-Handmade-Whitening/dp/B09S6M7JQJ/ref=zg_bs_c_beauty_d_sccl_1/259-6819556-7907717?pd_rd_w=IPkYQ&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B09S6M7JQJ&psc=1&tag=ankit007"
    },
    {
        title: "The Derma Co 1% Hyaluronic Sunscreen Aqua Gel SPF 50 PA++++ | For Oily, Dry, Acne-prone Skin | Ultra Lightweight Texture | Non-Greasy | No White Cast | Broad Spectrum Protection & Blue Light Protection | For Men & Women | 50 g",
        image: "https://images-eu.ssl-images-amazon.com/images/I/51x3cj+-iUL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Derma-Co-Hyaluronic-Sunscreen-Protection/dp/B095CRM8NF/ref=zg_bs_c_beauty_d_sccl_2/259-6819556-7907717?pd_rd_w=IPkYQ&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B095CRM8NF&psc=1&tag=ankit007"
    },
    {
        title: "Cetaphil Paraben, Sulphate-Free Gentle Skin Hydrating Face Wash Cleanser with Niacinamide, Vitamin B5 for Dry to Normal, Sensitive Skin - 125 ml",
        image: "https://images-eu.ssl-images-amazon.com/images/I/51O+J5jnXcL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Cetaphil-Sulphate-Free-Hydrating-Niacinamide-Sensitive/dp/B01CCGW4OE/ref=zg_bs_c_beauty_d_sccl_3/259-6819556-7907717?pd_rd_w=IPkYQ&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B01CCGW4OE&psc=1&tag=ankit007"
    },
    {
        title: "Simple Kind To Skin Refreshing Face Wash 150 ml | 100% soap-free gentle cleanser for sensitive, dry & oily skin, for women & men",
        image: "https://images-eu.ssl-images-amazon.com/images/I/51lV2Pem64L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Simple-Kind-Refreshing-Facial-Globalbeauty/dp/B000LQUA6M/ref=zg_bs_c_beauty_d_sccl_4/259-6819556-7907717?pd_rd_w=IPkYQ&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B000LQUA6M&psc=1&tag=ankit007"
    },
    {
        title: "Be Bodywise 4% Aha Bha Underarm Roll On 50ml | 2% Lactic Acid, 1% Mandelic Acid, 1% Salicylic Acid | Controls Odour & Reduces Pigmentation | 0% Alcohol & 0% Aluminium | Flora Fragrance",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71waYmGy3EL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Be-Bodywise-Salicylic-Pigmentation-Fragrance/dp/B0BRJWZNVM/ref=zg_bs_c_beauty_d_sccl_5/259-6819556-7907717?pd_rd_w=IPkYQ&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B0BRJWZNVM&psc=1&tag=ankit007"
    },
    {
        title: "DOT & KEY Vitamin C + E Super Bright Sunscreen Spf 50 |Water-Light,UVA/UVB & Blue Light Protection|For Even Toned & Glowing Skin|With Liquid Spf 50+++| No White Cast| For All Skin Types| 50G,Pack Of 1",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61UGAajCkwL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestseller",
        type: "Bestseller",
        link: "https://www.amazon.in/Vitamin-Sunscreen-Water-Light-Protection-Absorption/dp/B0BLK4YRSN/ref=zg_bs_c_beauty_d_sccl_6/259-6819556-7907717?pd_rd_w=IPkYQ&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=5WAKWA6XYTPXBMY4S3NS&pd_rd_wg=TIV7S&pd_rd_r=6277f612-1560-4029-a00f-ae2fd4ea76c4&pd_rd_i=B0BLK4YRSN&psc=1&tag=ankit007"
    },
];
