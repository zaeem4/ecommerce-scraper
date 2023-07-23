# import uvicorn
# pip3 install selenium
# pip3 install webdriver_manager
# sudo apt install chromium-chromedriver
# cp /usr/lib/chromium-browser/chromedriver /usr/bin
# pip3 install validators
# conda install -c conda-forge pyjwt
# conda install -c conda-forge python-decouple
# pip3 install "pydantic[email]"
# pip3 install sqlalchemy

# ?check_same_thread=False

from fastapi import FastAPI, Form, Body, Depends, HTTPException, Request, Response

from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep

import urllib.parse as UrlParser
import validators

from model.User import Base
from model.UserSchema import UserSchema, UserLoginSchema, UserInfo
from auth.auth_bearer import JWTBearer
from auth.auth_handler import signJWT

from database.database import db_engine, SessionLocal
from sqlalchemy.orm import Session


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--enable-javascript")

chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
)

Base.metadata.create_all(bind=db_engine)

app = FastAPI(debug=True)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


def browser_script():
    browser = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )

    browser.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        Object.defineProperty(navigator, 'plugins', {
                get: function() { return {"0":{"0":{}},"1":{"0":{}},"2":{"0":{},"1":{}}}; }
        });
        Object.defineProperty(navigator, 'languages', {
            get: () => ["en-US", "en"]
        });
        Object.defineProperty(navigator, 'mimeTypes', {
            get: function() { return {"0":{},"1":{},"2":{},"3":{}}; }
        });

        window.screenY=23;
        window.screenTop=23;
        window.outerWidth=1337;
        window.outerHeight=825;
        window.chrome =
        {
        app: {
            isInstalled: false,
        },
        webstore: {
            onInstallStageChanged: {},
            onDownloadProgress: {},
        },
        runtime: {
            PlatformOs: {
            MAC: 'mac',
            WIN: 'win',
            ANDROID: 'android',
            CROS: 'cros',
            LINUX: 'linux',
            OPENBSD: 'openbsd',
            },
            PlatformArch: {
            ARM: 'arm',
            X86_32: 'x86-32',
            X86_64: 'x86-64',
            },
            PlatformNaclArch: {
            ARM: 'arm',
            X86_32: 'x86-32',
            X86_64: 'x86-64',
            },
            RequestUpdateCheckStatus: {
            THROTTLED: 'throttled',
            NO_UPDATE: 'no_update',
            UPDATE_AVAILABLE: 'update_available',
            },
            OnInstalledReason: {
            INSTALL: 'install',
            UPDATE: 'update',
            CHROME_UPDATE: 'chrome_update',
            SHARED_MODULE_UPDATE: 'shared_module_update',
            },
            OnRestartRequiredReason: {
            APP_UPDATE: 'app_update',
            OS_UPDATE: 'os_update',
            PERIODIC: 'periodic',
            },
        },
        };
        window.navigator.chrome =
        {
        app: {
            isInstalled: false,
        },
        webstore: {
            onInstallStageChanged: {},
            onDownloadProgress: {},
        },
        runtime: {
            PlatformOs: {
            MAC: 'mac',
            WIN: 'win',
            ANDROID: 'android',
            CROS: 'cros',
            LINUX: 'linux',
            OPENBSD: 'openbsd',
            },
            PlatformArch: {
            ARM: 'arm',
            X86_32: 'x86-32',
            X86_64: 'x86-64',
            },
            PlatformNaclArch: {
            ARM: 'arm',
            X86_32: 'x86-32',
            X86_64: 'x86-64',
            },
            RequestUpdateCheckStatus: {
            THROTTLED: 'throttled',
            NO_UPDATE: 'no_update',
            UPDATE_AVAILABLE: 'update_available',
            },
            OnInstalledReason: {
            INSTALL: 'install',
            UPDATE: 'update',
            CHROME_UPDATE: 'chrome_update',
            SHARED_MODULE_UPDATE: 'shared_module_update',
            },
            OnRestartRequiredReason: {
            APP_UPDATE: 'app_update',
            OS_UPDATE: 'os_update',
            PERIODIC: 'periodic',
            },
        },
        };
        ['height', 'width'].forEach(property => {
            const imageDescriptor = Object.getOwnPropertyDescriptor(HTMLImageElement.prototype, property);

            // redefine the property with a patched descriptor
            Object.defineProperty(HTMLImageElement.prototype, property, {
                ...imageDescriptor,
                get: function() {
                    // return an arbitrary non-zero dimension if the image failed to load
                if (this.complete && this.naturalHeight == 0) {
                    return 20;
                }
                    return imageDescriptor.get.apply(this);
                },
            });
        });

        const getParameter = WebGLRenderingContext.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) {
                return 'Intel Open Source Technology Center';
            }
            if (parameter === 37446) {
                return 'Mesa DRI Intel(R) Ivybridge Mobile ';
            }

            return getParameter(parameter);
        };

        const elementDescriptor = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'offsetHeight');

        Object.defineProperty(HTMLDivElement.prototype, 'offsetHeight', {
            ...elementDescriptor,
            get: function() {
                if (this.id === 'modernizr') {
                return 1;
                }
                return elementDescriptor.get.apply(this);
            },
        });
        """
        },
    )

    return browser


# def get_db():
#     """
#     Method to generate database session
#     :return: Session
#     """
#     db = None
#     try:
#         db = Session()
#         yield db
#     finally:
#         db.close()


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


# Dependency
def get_db(request: Request):
    return request.state.db


@app.get("/")
def root():
    return {"status": "Scraper is up"}


@app.post("/find", dependencies=[Depends(JWTBearer())], tags=["scrapy"])
async def findById(webName: str = Form(), id: str = Form()):
    try:
        if " " in id:
            return {"success": False, "error": "Enter correct input"}

        if validators.url(id):
            return {"success": False, "error": "Only id is acceptable"}

        browser = browser_script()

        if webName == "www2.cip1.com":
            try:
                web = "https://www2.cip1.com/"

                browser.get(web)
                browser.implicitly_wait(5)

                search_box = browser.find_element(By.ID, "search_query")
                search_box.send_keys(id)

                sleep(1)

                search_button = browser.find_element(By.CLASS_NAME, "headersearch-icon")
                search_button.click()

                browser.implicitly_wait(5)
                sleep(3)

                if browser.title == "Just a moment...":
                    # browser.get(browser.current_url)
                    # browser.implicitly_wait(5)
                    browser.quit()
                    return {"success": False, "error": "Cloudfare blockage"}
            except Exception as e:
                browser.quit()
                return {"success": False, "error": "product not found | 4", "e": e}

            try:
                if wait(browser, 10).until(
                    EC.presence_of_all_elements_located(
                        (
                            By.XPATH,
                            '//ul[contains(@class, "snize-search-results-content")]',
                        )
                    )
                ):
                    try:
                        li = browser.find_elements(
                            By.XPATH,
                            '//ul/li[contains(@class,"snize-product snize-product-in-stock")]',
                        )

                        if li and len(li) > 0:
                            item = li[0]

                            href_link = item.find_element(
                                By.XPATH, "./a"
                            ).get_attribute("href")

                            img_link = item.find_element(
                                By.XPATH, "./*/*/div/*/img"
                            ).get_attribute("src")

                            prod_price = item.find_element(
                                By.XPATH, "./*/*/span/div"
                            ).text

                            prod_title = item.find_element(
                                By.XPATH, "./*/*/span/span"
                            ).text

                            browser.quit()
                            return {
                                "success": True,
                                "img_link": img_link,
                                "prod_title": prod_title,
                                "prod_price": prod_price,
                                "product_link": href_link,
                            }
                        else:
                            browser.quit()
                            return {"success": False, "error": "Product not found. | 1"}
                    except Exception as e:
                        browser.quit()
                        return {"success": False, "error": "Product not found. | 3"}

            except Exception as e:
                browser.quit()
                return {"success": False, "error": "Product not found. | 2", "e": e}

        elif webName == "www.ebay.com":
            try:
                web = "https://www.ebay.com"

                browser.get(web)
                browser.implicitly_wait(5)

                search_box = browser.find_element(
                    By.CLASS_NAME, "ui-autocomplete-input"
                )
                search_box.send_keys(id)

                sleep(1)

                search_button = browser.find_element(By.ID, "gh-btn")
                search_button.click()

                browser.implicitly_wait(5)
                sleep(3)

                if browser.title == "Just a moment...":
                    # browser.get(browser.current_url)
                    # browser.implicitly_wait(5)
                    browser.quit()
                    return {"success": False, "error": "Cloudfare blockage"}

            except Exception as e:
                browser.quit()
                return {"success": False, "error": "product not found | 4", "e": e}

            try:
                if wait(browser, 10).until(
                    EC.presence_of_all_elements_located(
                        (
                            By.XPATH,
                            '//ul[contains(@class, "srp-results srp-list")]',
                        )
                    )
                ):
                    try:
                        li = browser.find_elements(
                            By.XPATH,
                            '//ul/li[contains(@class,"s-item__pl-on-bottom")]',
                        )

                        if li and len(li) > 0:
                            item = li[0]
                            href_link = item.find_element(
                                By.XPATH,
                                "./*/div[1]/*/a",
                            ).get_attribute("href")
                            img_link = item.find_element(
                                By.XPATH,
                                "./*/div[1]/*/a/*/img",
                            ).get_attribute("src")
                            prod_price = item.find_element(
                                By.XPATH,
                                './*/div[2]/div[contains(@class, "s-item__details")]/div[1]/span',
                            ).text
                            prod_title = item.find_element(
                                By.XPATH,
                                "./*/div[2]/a/div/span",
                            ).text

                            browser.quit()
                            return {
                                "success": True,
                                "img_link": img_link,
                                "prod_title": prod_title,
                                "prod_price": prod_price,
                                "product_link": href_link,
                            }
                        else:
                            browser.quit()
                            return {"success": False, "error": "Product not found. | 1"}
                    except Exception as e:
                        browser.quit()
                        return {
                            "success": False,
                            "error": "Product not found. | 3",
                            "e": e,
                        }

            except Exception as e:
                try:
                    if wait(browser, 10).until(
                        EC.presence_of_all_elements_located(
                            (
                                By.XPATH,
                                '//ul[contains(@class, "srp-results srp-grid")]',
                            )
                        )
                    ):
                        try:
                            li = browser.find_elements(
                                By.XPATH,
                                '//ul/li[contains(@class,"s-item__pl-on-bottom")]',
                            )

                            if li and len(li) > 0:
                                item = li[0]
                                href_link = item.find_element(
                                    By.XPATH,
                                    "./*/div[1]/*/a",
                                ).get_attribute("href")
                                img_link = item.find_element(
                                    By.XPATH,
                                    "./*/div[1]/*/a/*/img",
                                ).get_attribute("src")
                                prod_price = item.find_element(
                                    By.XPATH,
                                    "./*/div[2]/div[contains(@class, 's-item__details')]/div[1]/span",
                                ).text
                                prod_title = item.find_element(
                                    By.XPATH,
                                    "./*/div[2]/a/div/span",
                                ).text

                                browser.quit()
                                return {
                                    "success": True,
                                    "img_link": img_link,
                                    "prod_title": prod_title,
                                    "prod_price": prod_price,
                                    "product_link": href_link,
                                }
                            else:
                                browser.quit()
                                return {
                                    "success": False,
                                    "error": "Product not found. | 1",
                                }
                        except Exception as e:
                            browser.quit()
                            return {
                                "success": False,
                                "error": "Product not found. | 3",
                                "e": e,
                            }

                except Exception as e:
                    browser.quit()
                    return {"success": False, "error": "Product not found. | 2", "e": e}

        elif webName == "www.partzilla.com":
            web = f"https://www.partzilla.com/search?q={id}&ui=typeahead"

            # browser.get(web)
            # browser.implicitly_wait(5)

            # search_box = browser.find_element(By.CLASS_NAME, "search-input")
            # search_box.send_keys(id)

            # sleep(3)

            # search_button = browser.find_element(By.CLASS_NAME, "search-button")
            # search_button.click()

            # browser.implicitly_wait(5)
            # sleep(3)

            # if browser.title == "Just a moment...":
            browser.get(web)
            browser.implicitly_wait(5)

            try:
                if wait(browser, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, '//div[contains(@class, "product-cards")]')
                    )
                ):
                    try:
                        li = browser.find_elements(
                            By.XPATH, '//div[contains(@class,"product-card-container")]'
                        )

                        if li and len(li) > 0:
                            item = li[0]
                            href_link = item.find_element(
                                By.XPATH, "./*/div[1]/a"
                            ).get_attribute("href")
                            img_link = item.find_element(
                                By.XPATH, "./*/div[1]/a/div"
                            ).get_attribute("style")

                            img_link = (
                                img_link.replace("background-image: url(", "")
                                .replace('"', "")
                                .replace(")", "")
                                .replace(";", "")
                            )

                            prod_price = item.find_element(
                                By.XPATH, "./*/div[2]/*/div[1]/*/div[1]/*"
                            ).text

                            prod_title = item.find_element(
                                By.XPATH, "./*/div[1]/div/a"
                            ).text

                            browser.quit()
                            return {
                                "success": True,
                                "img_link": img_link,
                                "prod_title": prod_title,
                                "prod_price": prod_price,
                                "product_link": href_link,
                            }
                        else:
                            browser.quit()
                            return {"success": False, "error": "Product not found. | 1"}
                    except Exception as e:
                        browser.quit()
                        return {
                            "success": False,
                            "error": "Product not found. | 3",
                            "e": e,
                        }
            except Exception as e:
                browser.quit()
                return {"success": False, "error": "Product not found. | 2", "e": e}

        elif webName == "partsouq.com":
            web = f"https://partsouq.com/en/search/all?q={id}"

            # browser.get(web)
            # browser.implicitly_wait(5)

            # search_box = browser.find_element(By.XPATH, "//input[@name='q']")
            # search_box.send_keys(id)

            # sleep(3)

            # search_button = browser.find_element(
            #     By.XPATH, '//button[contains(@class,"btn btn-success btn-sm")]'
            # )
            # search_button.click()

            # if browser.title == "Just a moment...":

            browser.get(web)
            browser.implicitly_wait(2)

            try:
                if wait(browser, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, '//div[contains(@class, "search-result-container")]')
                    )
                ):
                    try:
                        li = browser.find_elements(
                            By.XPATH,
                            '//div[contains(@class,"table-responsive search-result-vin search-catalog")]',
                        )

                        if li and len(li) > 0:
                            item = li[0]
                            img_link = item.find_element(
                                By.XPATH, "./*/*/tr[2]/td[1]/img"
                            ).get_attribute("src")
                            prod_title = item.find_element(
                                By.XPATH, "./*/div[3]/*/div[2]/*/span"
                            ).text

                            product_link = browser.current_url

                            browser.quit()

                            return {
                                "success": True,
                                "img_link": img_link,
                                "prod_title": prod_title,
                                "product_link": product_link,
                                "prod_discription": "",
                                "prod_price": "",
                            }

                        li = browser.find_elements(
                            By.XPATH,
                            '//div[contains(@class,"product-col list clearfix")]',
                        )

                        if li and len(li) > 0:
                            item = li[0]
                            img_link = item.find_element(
                                By.XPATH, "./*/div[1]/*/a"
                            ).get_attribute("href")
                            prod_price = item.find_element(
                                By.XPATH, "./*/div[3]/*/div[2]/*/span"
                            ).text
                            prod_title = item.find_element(
                                By.XPATH, "./*/div[2]/*/h1"
                            ).text

                            product_link = browser.current_url

                            browser.quit()

                            return {
                                "success": True,
                                "img_link": img_link,
                                "prod_price": prod_price,
                                "prod_title": prod_title,
                                "product_link": product_link,
                                "prod_discription": "",
                            }
                        else:
                            browser.quit()
                            return {"success": False, "error": "Product not found. | 1"}

                        print(6)
                    except Exception as e:
                        browser.quit()
                        return {
                            "success": False,
                            "error": "Product not found. | 3",
                            "e": e,
                        }
            except Exception as e:
                browser.quit()
                return {"success": False, "error": "Product not found. | 2", "e": e}

        elif webName == "www.aliexpress.com":
            web = "https://www.aliexpress.com"

            browser.get(web)
            browser.implicitly_wait(5)

            search_box = browser.find_element(By.ID, "search-key")
            search_box.send_keys(id)

            sleep(1)

            search_button = browser.find_element(By.CLASS_NAME, "search-button")
            search_button.click()

            browser.implicitly_wait(5)
            sleep(5)

            if browser.title == "Just a moment...":
                # url = browser.current_url
                # browser.quit()
                # sleep(1)
                # browser.get(url)
                # browser.implicitly_wait(5)
                return {"success": False, "error": "Cloudfare blockage"}
            try:
                if wait(browser, 10).until(
                    EC.presence_of_all_elements_located((By.ID, "card-list"))
                ):
                    try:
                        li = browser.find_elements(
                            By.XPATH, '//a[contains(@class,"search-card-item")]'
                        )

                        if li and len(li) > 0:
                            item = li[0]

                            href_link = item.get_attribute("href")

                            img_link = item.find_element(
                                By.XPATH,
                                "./div[1]/img",
                            ).get_attribute("src")

                            prod_price = item.find_element(
                                By.XPATH,
                                "./div[2]/div[1]",
                            ).text

                            prod_title = item.find_element(
                                By.XPATH,
                                "./div[2]/div[4]/*",
                            ).text
                            browser.quit()

                            return {
                                "success": True,
                                "img_link": img_link,
                                "prod_price": prod_price,
                                "prod_title": prod_title,
                                "product_link": href_link,
                            }
                        else:
                            browser.quit()
                            return {"success": False, "error": "Product not found. | 1"}
                    except Exception as e:
                        browser.quit()
                        return {
                            "success": False,
                            "error": "Product not found. | 3",
                            "e": e,
                        }
            except Exception as e:
                browser.quit()
                return {"success": False, "error": "Product not found. | 2", "e": e}

        elif webName == "amazon.com":
            web = f"https://www.amazon.com/s?k={id}"
            # web = "https://www.amazon.com"

            # browser.get(web)
            # browser.implicitly_wait(5)

            # search_box = browser.find_element(By.ID, "twotabsearchtextbox")
            # search_box.send_keys(id)

            # sleep(1)

            # search_button = browser.find_element(By.ID, "nav-search-submit-button")
            # search_button.click()

            # browser.implicitly_wait(5)
            # sleep(3)

            # if browser.title == "Just a moment...":
            #     # url = browser.current_url
            #     # browser.quit()
            #     # sleep(3)
            #     # browser.get(url)
            #     # browser.implicitly_wait(5)
            #     return {"success": False, "error": "Cloudfare blockage"}

            browser.get(web)
            browser.implicitly_wait(5)

            try:
                if wait(browser, 10).until(
                    EC.presence_of_all_elements_located(
                        (
                            By.XPATH,
                            '//div[contains(@class, "s-main-slot s-result-list s-search-results sg-row")]',
                        )
                    )
                ):
                    try:
                        li = browser.find_elements(
                            By.XPATH,
                            '//div[contains(@data-component-type, "s-search-result")]',
                        )

                        if li and len(li) > 0:
                            item = li[0]

                            href_link = item.find_element(
                                By.XPATH,
                                "./*/*/*/*/div[1]/*/a",
                            ).get_attribute("href")

                            img_link = item.find_element(
                                By.XPATH,
                                "./*/*/*/*/div[1]/*/a/*/img",
                            ).get_attribute("src")

                            prod_price = item.find_element(
                                By.XPATH,
                                "./*/*/*/*/div[2]",
                            ).text

                            # prod_price = prod_price[0].text

                            # prod_title = item.find_elements(
                            #     By.XPATH,
                            #     "./*/*/*/*/div[2]/div[contains(@class, 'a-section a-spacing-none a-spacing-top-small s-price-instructions-style')]",
                            # )

                            browser.quit()

                            return {
                                "success": True,
                                "img_link": img_link,
                                "prod_price": prod_price,
                                # "prod_title": prod_title,
                                "product_link": href_link,
                            }
                        else:
                            browser.quit()
                            return {"success": False, "error": "Product not found. | 1"}

                    except Exception as e:
                        browser.quit()
                        return {
                            "success": False,
                            "error": "Product not found. | 3",
                            "e": e,
                        }
            except Exception as e:
                browser.quit()
                return {"success": False, "error": "Product not found. | 2", "e": e}

        browser.quit()
        return {"success": False, "error": "website template not exists"}
    except Exception as e:
        return {"success": False, "error": "unable to process req", "e": e}


@app.post("/get", dependencies=[Depends(JWTBearer())], tags=["scrapy"])
async def findByUrl(url: str = Form()):
    if not validators.url(url):
        return {"success": False, "error": "Enter correct input"}

    net_loc = UrlParser.urlparse(url).netloc

    if net_loc == "www2.cip1.com":
        try:
            browser = browser_script()

            browser.get(url)
            browser.implicitly_wait(5)

            if wait(browser, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//div[contains(@class, "productView")]')
                )
            ):
                try:
                    img_link = browser.find_element(
                        By.XPATH,
                        '//*[@id="main-content"]/div[1]/div/div[1]/section[1]/div[2]/figure/div/a/img',
                    ).get_attribute("src")

                    prod_discription = browser.find_element(
                        By.XPATH,
                        '//*[@id="main-content"]/div[1]/div/div[1]/article/div',
                    ).text

                    prod_title = browser.find_element(
                        By.XPATH,
                        '//*[@id="main-content"]/div[1]/div/div[1]/section[2]/div[2]/h1',
                    ).text

                    prod_price = browser.find_element(
                        By.XPATH,
                        '//*[@id="main-content"]/div[1]/div/div[1]/section[2]/div[2]/div[2]',
                    ).text

                    browser.quit()
                    return {
                        "success": True,
                        "img_link": img_link,
                        "prod_discription": prod_discription,
                        "prod_title": prod_title,
                        "prod_price": prod_price,
                    }

                except Exception as e:
                    browser.quit()
                    return {"success": False, "error": "Product not found. | 3"}
            else:
                browser.quit()
                return {"success": False, "error": "Product not found. | 2"}
        except Exception as e:
            browser.quit()
            return {"success": False, "error": e}

    elif net_loc == "www.ebay.com":
        try:
            browser = browser_script()

            browser.get(url)
            browser.implicitly_wait(5)

            if wait(browser, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//div[contains(@id, "LeftSummaryPanel")]')
                )
            ):
                try:
                    img_link = browser.find_element(
                        By.XPATH,
                        '//*[@id="mainImgHldr"]/div[1]/div/div[1]/div/div/img',
                    ).get_attribute("src")

                    prod_discription = browser.find_element(
                        By.XPATH,
                        '//*[@id="viTabs_0_is"]/div',
                    ).text

                    prod_title = browser.find_element(
                        By.XPATH,
                        '//*[@id="LeftSummaryPanel"]/div[1]/div[1]/div/h1/span',
                    ).text

                    prod_price = browser.find_element(
                        By.XPATH,
                        '//*[@id="mainContent"]/form/div[2]/div/div[1]/div[1]/div/div[2]',
                    ).text

                    browser.quit()
                    return {
                        "success": True,
                        "img_link": img_link,
                        "prod_discription": prod_discription,
                        "prod_title": prod_title,
                        "prod_price": prod_price,
                    }

                except Exception as e:
                    browser.quit()
                    return {"success": False, "error": "Product not found. | 3"}
            else:
                browser.quit()
                return {"success": False, "error": "Product not found. | 2"}
        except Exception as e:
            browser.quit()
            return {"success": False, "error": e}

    elif net_loc == "www.partzilla.com":
        try:
            browser = browser_script()

            browser.get(url)
            browser.implicitly_wait(5)

            if wait(browser, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//div[contains(@class, "product")]')
                )
            ):
                try:
                    img_link = browser.find_element(
                        By.XPATH,
                        "/html/body/section[2]/div/div/div[1]/div[1]/div/img",
                    ).get_attribute("src")

                    prod_discription = browser.find_element(
                        By.XPATH,
                        "/html/body/section[2]/div/div/div[2]/div[1]",
                    ).text

                    prod_title = browser.find_element(
                        By.XPATH,
                        "/html/body/section[2]/div/div/div[1]/div[2]/h1",
                    ).text

                    prod_price = browser.find_element(
                        By.XPATH,
                        "/html/body/section[2]/div/div/div[1]/div[2]/div[2]/span",
                    ).text

                    browser.quit()
                    return {
                        "success": True,
                        "img_link": img_link,
                        "prod_discription": prod_discription,
                        "prod_title": prod_title,
                        "prod_price": prod_price,
                    }

                except Exception as e:
                    browser.quit()
                    return {"success": False, "error": "Product not found. | 3"}
            else:
                browser.quit()
                return {"success": False, "error": "Product not found. | 2"}
        except Exception as e:
            browser.quit()
            return {"success": False, "error": e}

    elif net_loc == "partsouq.com":
        try:
            browser = browser_script()

            browser.get(url)
            browser.implicitly_wait(5)

            if wait(browser, 10).until(
                EC.presence_of_all_elements_located(
                    (
                        By.XPATH,
                        '//div[contains(@class,"table-responsive search-result-vin search-catalog")]',
                    )
                )
            ):
                try:
                    img_link = browser.find_element(
                        By.XPATH,
                        '//*[@id="content"]/div/div[1]/div/div[2]/div/div/table/tbody/tr[2]/td[1]/img',
                    ).get_attribute("src")

                    # prod_discription = browser.find_element(
                    #     By.XPATH,
                    #     "/html/body/section[2]/div/div/div[2]/div[1]",
                    # ).text

                    prod_title = browser.find_element(
                        By.XPATH,
                        '//*[@id="content"]/div/div[1]/div/div[2]/div/div/table/tbody/tr[2]/td[2]',
                    ).text

                    # prod_price = browser.find_element(
                    #     By.XPATH,
                    #     "/html/body/section[2]/div/div/div[1]/div[2]/div[2]/span",
                    # ).text

                    browser.quit()
                    return {
                        "success": True,
                        "img_link": img_link,
                        "prod_title": prod_title,
                        "prod_discription": "",
                        "prod_price": "",
                    }

                except Exception as e:
                    browser.quit()
                    return {"success": False, "error": "Product not found. | 3"}
            else:
                browser.quit()
                return {"success": False, "error": "Product not found. | 2"}
        except Exception as e:
            browser.quit()
            return {"success": False, "error": e}

    elif net_loc == "www.aliexpress.com":
        try:
            browser = browser_script()

            browser.get(url)
            browser.implicitly_wait(5)

            try:
                if wait(browser, 10).until(
                    EC.presence_of_all_elements_located(
                        (
                            By.XPATH,
                            '//div[contains(@class,"pdp-info")]',
                        )
                    )
                ):
                    try:
                        img_link = browser.find_element(
                            By.XPATH,
                            '//*[@id="pdp-main-image"]/div/div/div[1]/img',
                        ).get_attribute("src")

                        # prod_discription = browser.find_element(
                        #     By.XPATH,
                        #     '//*[@id="product-description"]/div/div[contains(@class,"detailmodule_html")]/div/div/span[1]/span',
                        # ).text

                        prod_title = browser.find_element(
                            By.XPATH,
                            '//*[@id="root"]/div[3]/div[1]/div[1]/div[2]/div[1]/h1',
                        ).text

                        prod_price = browser.find_element(
                            By.XPATH,
                            '//div[contains(@class,"product-price-current")]/div',
                        ).text

                        browser.quit()
                        return {
                            "success": True,
                            "img_link": img_link,
                            "prod_title": prod_title,
                            "prod_discription": "",
                            "prod_price": prod_price,
                        }

                    except Exception as e:
                        browser.quit()
                        return {
                            "success": False,
                            "error": "Product not found. | 3",
                            "e": e,
                        }
            except Exception as e:
                browser.quit()
                return {"success": False, "error": "Product not found. | 2", "e": e}
        except Exception as e:
            browser.quit()
            return {"success": False, "error": e}

    elif net_loc == "www.amazon.com":
        try:
            browser = browser_script()

            browser.get(url)
            browser.implicitly_wait(5)

            try:
                if wait(browser, 10).until(
                    EC.presence_of_all_elements_located(
                        (
                            By.XPATH,
                            '//div[contains(@id,"ppd")]',
                        )
                    )
                ):
                    try:
                        img_link = browser.find_element(
                            By.XPATH,
                            '//*[@id="landingImage"]',
                        ).get_attribute("src")

                        prod_discription = browser.find_element(
                            By.XPATH,
                            '//*[@id="feature-bullets"]',
                        ).text

                        prod_title = browser.find_element(
                            By.XPATH,
                            '//*[@id="productTitle"]',
                        ).text

                        prod_price = browser.find_element(
                            By.XPATH,
                            '//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]',
                        ).text

                        browser.quit()
                        return {
                            "success": True,
                            "img_link": img_link,
                            "prod_title": prod_title,
                            "prod_discription": prod_discription,
                            "prod_price": prod_price,
                        }

                    except Exception as e:
                        browser.quit()
                        return {
                            "success": False,
                            "error": "Product not found. | 3",
                            "e": e,
                        }
            except Exception as e:
                browser.quit()
                return {"success": False, "error": "Product not found. | 2", "e": e}
        except Exception as e:
            browser.quit()
            return {"success": False, "error": e}

    else:
        return {"success": False, "error": "Website template is not set"}


# @app.post("/user/signup", tags=["user"])
# async def create_user(user: UserSchema = Body(...), db: Session = Depends(get_db)):
#     dbResponse = UserInfo.create_user(user, db)
#     if dbResponse["success"]:
#         return signJWT(dbResponse["user"].email)
#     else:
#         return dbResponse


@app.post("/user/login", tags=["user"])
async def user_login(user: UserLoginSchema = Body(...), db: Session = Depends(get_db)):
    if UserInfo.check_user(user, db):
        return signJWT(user.email)

    return {"success": False, "error": "Wrong login details!"}


# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)
# uvicorn main:app --reload
