from tkcalendar import DateEntry
from tkinter import messagebox
from datetime import datetime
import customtkinter as ctk
from database import add_product, get_products, delete_product, update_product

ctk.set_appearance_mode("light")

app = ctk.CTk()
app.title("FreshTrack")
app.geometry("700x500+900+100")

def update_dashboard():

    products = get_products()

    total = len(products)
    expiring = 0
    expired = 0

    today = datetime.now().date()

    for product in products:

        expiry = datetime.strptime(product[2],"%d/%m/%Y").date()

        days_left = (expiry - today).days

        if days_left < 0:
            expired += 1

        elif days_left <= product[3]:
            expiring += 1

    total_label.configure(text=f"📦 Total: {total}")
    expiring_label.configure(text=f"🟠 Expiring: {expiring}")
    expired_label.configure(text=f"🔴 Expired: {expired}")


def add_fruit():

    window = ctk.CTkToplevel(app)
    window.lift()
    window.focus_force()
    window.title("Add Fruit / Vegetable")
    window.geometry("500x600+50+100")

    category_var = ctk.StringVar(value="Fruits")

    ctk.CTkLabel(window,text="Category").pack(pady=10)

    category_menu = ctk.CTkOptionMenu(
        window,
        values=[
            "Fruits",
            "Vegetables",
            "Dairy",
            "Grains",
            "Nuts & Seeds",
            "Packaged Food"
        ],
        variable=category_var
    )

    category_menu.pack(pady=5)

    ctk.CTkLabel(window,text="Item Name").pack(pady=10)

    item_entry = ctk.CTkEntry(window)
    item_entry.pack(pady=5)
    
    ctk.CTkLabel(window,text="Expiry Date").pack(pady=10)

    expiry_entry = DateEntry(
        window,
        date_pattern="dd/mm/yyyy")

    expiry_entry.pack(pady=5)
    
    ctk.CTkLabel(window,text="Reminder Days").pack(pady=10)

    days_entry = ctk.CTkEntry(window)
    days_entry.pack(pady=5)

    def save_item():
        
        category = category_var.get().strip()
        item = item_entry.get().strip()
        expiry = expiry_entry.get()
        days = days_entry.get().strip()

        if item == "" or expiry == "" or days == "":
            messagebox.showerror(
                "Error",
                "Please fill all fields"
            )
            return
            
        add_product(
            category,
            item,
            expiry,
            int(days)
        )
        update_dashboard()
        item_entry.delete(0,"end")
        expiry_entry.delete(0,"end")
        days_entry.delete(0,"end")
        
        print("SAVE BUTTON CLICKED")
        
        messagebox.showinfo(
            "Success",
            "Product Saved Successfully!"
        )
        
    ctk.CTkButton(
        window,
        text = "💾 Save",
        command = save_item
    ).pack(pady = 20)
    
def delete_and_refresh(name, window):

    delete_product(name)
    update_dashboard()

    messagebox.showinfo(
        "Deleted",
        f"{name} deleted successfully"
    )

    window.destroy()

    view_items()
    
def edit_product(name, old_expiry, old_reminder,parent_window):

    edit_window = ctk.CTkToplevel(app)
    edit_window.title(f"Edit {name}")
    edit_window.geometry("350x250+600+100")

    ctk.CTkLabel(
        edit_window,
        text="New Expiry Date"
    ).pack(pady=10)

    expiry_entry = ctk.CTkEntry(edit_window)
    expiry_entry.pack()
    expiry_entry.insert(0, old_expiry)

    ctk.CTkLabel(
        edit_window,
        text="New Reminder Days"
    ).pack(pady=10)

    reminder_entry = ctk.CTkEntry(edit_window)
    reminder_entry.pack()
    reminder_entry.insert(0, str(old_reminder))

    def save_changes():

        update_product(
            name,
            expiry_entry.get(), update_dashboard(),
            int(reminder_entry.get())
        )

        messagebox.showinfo(
            "Success",
            f"{name} updated successfully!"
        )

        edit_window.destroy()
        parent_window.destroy()
        view_items()

    ctk.CTkButton(
        edit_window,
        text="💾 Save Changes",
        command=save_changes
    ).pack(pady=20)
    
        
def view_items():

    window = ctk.CTkToplevel(app)
    window.title("Stored Items")
    window.geometry("400x400+50+100")
    
    scroll_frame = ctk.CTkScrollableFrame(
        window,
        width=350,
        height=350
    )

    scroll_frame.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    products = get_products()

    search_text = search_entry.get().lower()

    if search_text:
        products = [
            p for p in products
            if search_text in p[1].lower()
        ]

    products = sorted(
        products,
        key=lambda p: datetime.strptime(
            p[2],"%d/%m/%Y")
    )

    for product in products:
        
        print(product)
        
        expiry = datetime.strptime(
            product[2],
            "%d/%m/%Y"
        ).date()

        days_left = (expiry - datetime.now().date()).days
    
        print("Days left:",days_left)

        if days_left < 0:
            status = "🔴 Expired"
        elif days_left <= 7:
            status = "🟠 Expiring Soon"
        else:
            status = "🟢 Safe"

        text = f"""
        📂{product[0]}
        🍎{product[1]}
        🗓️{product[2]}
        ⏰Reminder:{product[3]}days
        """

        label = ctk.CTkLabel(
            scroll_frame,
            text=text
        )

        label.pack(pady=5)
        
        if days_left < 0:
            color = "red"
        elif days_left <= 7:
            color = "orange"
        else:
            color = "green"

        status_label = ctk.CTkLabel(
            scroll_frame,
            text=status,
            text_color=color
        )

        status_label.pack()
        
        name = product[1]
        
        ctk.CTkButton(
            scroll_frame,
            text=f"📝 Edit {name}",
            command=lambda n=name,
                   e=product[2],
                   r=product[3]:
                edit_product(n, e, r, window)
        ).pack(pady=2)

        ctk.CTkButton(
            scroll_frame,
            text=f"🗑 Delete {name}",
            command=lambda n=name: delete_and_refresh(n,window)
        ).pack(pady=2)
        
        
def check_expiry():
    
    print("CHECK_EXPIRY VERSION 2")

    window = ctk.CTkToplevel(app)
    window.title("Expiry Alerts")
    window.geometry("500x400+50+100")

    products = get_products()

    if len(products) == 0:

        ctk.CTkLabel(
            window,
            text="No products stored."
        ).pack(pady=20)

        return
    
    from datetime import datetime
    
    today = datetime.now().date()

    for product in products:
        print(product)
        
        try:

            expiry = datetime.strptime(
                product[2],
                "%d/%m/%Y"
            ).date()

            days_left = (expiry - today).days

            if days_left <= product[3]:

                text = f"⚠️ {product[1]} expires in {days_left} days"

                ctk.CTkLabel(
                    window,
                    text=text
                ).pack(pady=5)

        except Exception as e:
            print("ERROR:",e)

def show_dashboard():

    window = ctk.CTkToplevel(app)
    window.title("Dashboard")
    window.geometry("400x400")

    products = get_products()

    total_products = len(products)
    
    from datetime import datetime

    safe = 0
    expiring = 0
    expired = 0

    today = datetime.now().date()

    for product in products:
        
        try:
            expiry = datetime.strptime(
            product[2],
            "%d/%m/%Y"
            ).date()

            days_left = (expiry - today).days

            if days_left < 0:
                expired += 1

            elif days_left <= product[3]:
                expiring += 1

            else:
                safe += 1

        except:
            pass   
        
    ctk.CTkLabel(
        window,
        text=f"📦 Total Products: {total_products}",
        font=("Arial", 18, "bold")
    ).pack(pady=20)
    
    ctk.CTkLabel(
        window,
        text=f"🟢 Safe Products: {safe}",
        text_color="green",
        font=("Arial", 16)
    ).pack(pady=10)

    ctk.CTkLabel(
        window,
        text=f"🟡 Expiring Soon: {expiring}",
         text_color="orange",
        font=("Arial", 16)
    ).pack(pady=10)

    ctk.CTkLabel(
        window,
        text=f"🔴 Expired Products: {expired}",
         text_color="red",
        font=("Arial", 16)
    ).pack(pady=10)
    
def export_report():

    products = get_products()

    with open("FreshTrack_Report.csv", "w") as file:

        file.write(
            "Category,Item,Expiry Date,Reminder Days\n"
        )

        for product in products:

            file.write(
                f"{product[0]},{product[1]},{product[2]},{product[3]}\n"
            )

    messagebox.showinfo("Report Exported Successfully!", "Report Saved as:\nFreshTrack_Report.csv")

title = ctk.CTkLabel(
    app,
    text="FreshTrack",
    font=("Comic San", 30, "bold")
)
title.pack(pady=20)

dashboard_frame = ctk.CTkFrame(app, fg_color="transparent")
dashboard_frame.pack(pady=10)

total_label = ctk.CTkLabel(
    dashboard_frame,
    text="📦 Total: 0",
    font=("Arial", 16, "bold")
)
total_label.pack(side="left", padx=10)

expiring_label = ctk.CTkLabel(
    dashboard_frame,
    text="🟠 Expiring: 0",
    text_color="orange",
    font=("Arial", 16, "bold")
)
expiring_label.pack(side="left", padx=10)

expired_label = ctk.CTkLabel(
    dashboard_frame,
    text="🔴 Expired: 0",
    text_color="red",
    font=("Arial", 16, "bold")
)
expired_label.pack(side="left", padx=10)

search_entry = ctk.CTkEntry(
    app,
    placeholder_text="🔍 Search Product"
)

search_entry.pack(pady=10)

ctk.CTkButton(
    app,
    text="🍎 Add Fruit / Vegetable",
    command=add_fruit
).pack(pady=10)

ctk.CTkButton(
    app,
    text=" 📋View Stored Items",
    command=view_items
).pack(pady=10)

ctk.CTkButton(
    app,
    text="🔔 Check Expiring Soon",
    command=check_expiry
).pack(pady=10)

ctk.CTkButton(
    app,
    text="📄 Export Report",
    command=export_report
).pack(pady=10)

ctk.CTkButton(
    app,
    text = "📊 Dashboard",
    command = show_dashboard
).pack(pady=10)

update_dashboard()
app.mainloop()
