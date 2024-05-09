from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
import shutil
from pathlib import Path
@task
def order_robots_from_RobotSpareBin():
    open_robot_order_website()
   
    download_order_file()
    orders_list = get_orders()
    fillform(orders_list)
    archive_receipts()
 

def open_robot_order_website():
    browser.configure(slowmo =500,
                      )
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def close_annoying_modal():
    page = browser.page()
    page.click("//*[text()='OK']")

    

def download_order_file():
    http = HTTP()
    http.download(url = "https://robotsparebinindustries.com/orders.csv", overwrite=True)

def get_orders():
    tables = Tables()
    orderTable = tables.read_table_from_csv("orders.csv", header=True)
    return orderTable


def fillform(orders_list):

    for order in orders_list:
        close_annoying_modal()
        order_no = order["Order number"]
        head = order["Head"]
        body= order["Body"]
        legs = order["Legs"]
        address = order["Address"]
        page = browser.page()
        page.select_option("//select[@id = 'head']",head)
        page.click("//input[ @class ='form-check-input' and @value='"+body+"']")
        page.fill("//input[ @placeholder ='Enter the part number for the legs']", legs)
        page.fill("//input[ @placeholder ='Shipping address']",address)
        page.click("//button[ text()='Preview']")
        
        
        page.click("//button[@id = 'order' and @type= 'submit']")
        page = browser.page()
        for i in range(0,6):
            if page.is_visible("//div[@class = 'alert alert-danger']"):
                print("Error exists")
                page.click("//button[@id = 'order' and @type= 'submit']")
            else:
                print("No error")
        

            
        screenshpt_path = screenshot_robot(order_no)
        pdf_path = store_receipt_as_pdf(order_no)
        embed_screenshot_to_receipt(screenshpt_path,pdf_path)
        page.click("//button[@id = 'order-another' ]")



def screenshot_robot(order_no): 
    ss_path = "output/robot_image/screenshot_"+order_no+".png"
    page= browser.page()
    page.locator("//div[@id = 'robot-preview-image' ]").screenshot(path=ss_path)
    return ss_path

def store_receipt_as_pdf(order_number):
    page = browser.page()
    order_redeipt_html = page.locator("//div[@id = 'order-completion' ]").inner_html()
    path = "output/receipts/order_"+order_number+".pdf"
    pdf = PDF()
    pdf.html_to_pdf(order_redeipt_html, path)
    return path

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(
        image_path=screenshot,
        source_path=pdf_file,
        output_path=pdf_file
    )
    

def archive_receipts():
    archive_folder = "Output/archieved_orders"
    source_folder = Path("output/receipts")
    shutil.make_archive(archive_folder,"zip",source_folder)
    





