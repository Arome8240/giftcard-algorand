import { useState, useEffect } from 'react';
import { indexerClient, myAlgoConnect } from "./utils/constants";
import { v4 as uuidv4 } from "uuid";
import { stringToMicroAlgos, microAlgosToString } from './utils/conversions';
import './App.css';
import { buyGiftCardAction, createGiftCardAction, getgiftCardsAction, sellGiftCardAction } from './utils/marketplace';

function App() {
  const [address, setAddress] = useState(null);
  const [balance, setBalance] = useState(0);
  const [showDropDown, setShowDropDown] = useState(false);
  const [showGift, setShowGift] = useState(false);
  const [cards, setCards] = useState([]);
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");
  const [image, setImage] = useState("");

  const fetchBalance = async (accountAddress) => {
    indexerClient.lookupAccountByID(accountAddress).do()
      .then(response => {
        const _balance = response.account.amount;
        setBalance(_balance);
      })
      .catch(error => {
        console.log(error);
      });
  };

  const connectWallet = async () => {
    myAlgoConnect.connect()
      .then(accounts => {
        const _account = accounts[0];
        console.log(_account)
        setAddress(_account.address);
        fetchBalance(_account.address);
        if (_account.address) getGiftCards(_account.address);
      }).catch(error => {
        console.log('Could not connect to MyAlgo wallet');
        console.error(error);
      })
  };

  const createCard = async (number, description, image, amount) => {
    try {
      await createGiftCardAction(address, { number, amount: stringToMicroAlgos(amount), description, image })
      getGiftCards(address)
    } catch (error) {
      alert(error)
    }
    
  };

  const buyCard = async (card) => {
    buyGiftCardAction(address, card)
    .then(() => {
      getGiftCards(address);
      fetchBalance(address);
    })
    .catch(error => {
      console.log(error)
    })
  };

  const sellCard = async (card) => {
    sellGiftCardAction(address, card)
      .then(() => {
        getGiftCards(address);
        fetchBalance(address);
      })
      .catch(error => {
        console.log(error)
      })
  };

  const getGiftCards = async (_address) => {
    try {
      const card = await getgiftCardsAction();
      setCards(card);
    } catch (error) {
      alert(error)
      console.log(error);
    }

  };

  useEffect(() => {
    connectWallet()
  }, [])

  const formHandler = (event) => {
    event.preventDefault();
    const number = uuidv4();
    createCard(number, description, image, amount);
  };

  return (
    <div>
      <nav class="bg-white dark:bg-gray-800  shadow ">
        <div class="max-w-7xl mx-auto px-8">
          <div class="flex items-center justify-between h-16">
            <div class=" flex items-center">
              <a class="flex-shrink-0" href="/">
                <img
                  class="h-8 w-8"
                  src="https://www.logolynx.com/images/logolynx/d0/d0964c9931768f927c75eae0e021c949.png"
                  alt="Workflow"
                />
              </a>
              <div class="hidden md:block">
                <div class="ml-10 flex items-baseline space-x-4">
                  <a
                    class="text-gray-800 dark:text-white  hover:text-gray-800 dark:hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                    href="/#"
                  >
                    Home
                  </a>
                </div>
              </div>
            </div>
            <div class="block">
              <div class="ml-4 flex items-center md:ml-6">
                <a
                  href="https://github.com/"
                  class="p-1 rounded-full text-gray-400 focus:outline-none hover:text-gray-200 focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-white"
                >
                  <span class="sr-only">View github</span>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="30"
                    height="30"
                    fill="currentColor"
                    class="text-xl hover:text-gray-800 dark:hover:text-white transition-colors duration-200"
                    viewBox="0 0 1792 1792"
                  >
                    <path d="M896 128q209 0 385.5 103t279.5 279.5 103 385.5q0 251-146.5 451.5t-378.5 277.5q-27 5-40-7t-13-30q0-3 .5-76.5t.5-134.5q0-97-52-142 57-6 102.5-18t94-39 81-66.5 53-105 20.5-150.5q0-119-79-206 37-91-8-204-28-9-81 11t-92 44l-38 24q-93-26-192-26t-192 26q-16-11-42.5-27t-83.5-38.5-85-13.5q-45 113-8 204-79 87-79 206 0 85 20.5 150t52.5 105 80.5 67 94 39 102.5 18q-39 36-49 103-21 10-45 15t-57 5-65.5-21.5-55.5-62.5q-19-32-48.5-52t-49.5-24l-20-3q-21 0-29 4.5t-5 11.5 9 14 13 12l7 5q22 10 43.5 38t31.5 51l10 23q13 38 44 61.5t67 30 69.5 7 55.5-3.5l23-4q0 38 .5 88.5t.5 54.5q0 18-13 30t-40 7q-232-77-378.5-277.5t-146.5-451.5q0-209 103-385.5t279.5-279.5 385.5-103zm-477 1103q3-7-7-12-10-3-13 2-3 7 7 12 9 6 13-2zm31 34q7-5-2-16-10-9-16-3-7 5 2 16 10 10 16 3zm30 45q9-7 0-19-8-13-17-6-9 5 0 18t17 7zm42 42q8-8-4-19-12-12-20-3-9 8 4 19 12 12 20 3zm57 25q3-11-13-16-15-4-19 7t13 15q15 6 19-6zm63 5q0-13-17-11-16 0-16 11 0 13 17 11 16 0 16-11zm58-10q-2-11-18-9-16 3-14 15t18 8 14-14z"></path>
                  </svg>
                </a>
                <div class="ml-3 relative">
                  <div class="relative inline-block text-left">
                    <div>
                      <button
                        onClick={() => setShowDropDown((prev) => !prev)}
                        type="button"
                        class="  flex items-center justify-center  rounded-md  px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-50 hover:bg-gray-50 dark:hover:bg-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-100 focus:ring-gray-500"
                        id="options-menu"
                      >
                        <svg
                          width="20"
                          fill="currentColor"
                          height="20"
                          class="text-gray-800"
                          viewBox="0 0 1792 1792"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path d="M1523 1339q-22-155-87.5-257.5t-184.5-118.5q-67 74-159.5 115.5t-195.5 41.5-195.5-41.5-159.5-115.5q-119 16-184.5 118.5t-87.5 257.5q106 150 271 237.5t356 87.5 356-87.5 271-237.5zm-243-699q0-159-112.5-271.5t-271.5-112.5-271.5 112.5-112.5 271.5 112.5 271.5 271.5 112.5 271.5-112.5 112.5-271.5zm512 256q0 182-71 347.5t-190.5 286-285.5 191.5-349 71q-182 0-348-71t-286-191-191-286-71-348 71-348 191-286 286-191 348-71 348 71 286 191 191 286 71 348z"></path>
                        </svg>
                      </button>
                    </div>
                    {showDropDown && (
                      <div class="origin-top-right absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5">
                        <div
                          class="py-1 "
                          role="menu"
                          aria-orientation="vertical"
                          aria-labelledby="options-menu"
                        >
                          <a
                            href="#"
                            class="block block px-4 py-2 text-md text-gray-700 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-100 dark:hover:text-white dark:hover:bg-gray-600"
                            role="menuitem"
                          >
                            <span class="flex flex-col">
                              <span>Balance :{microAlgosToString(balance)} ALGO</span>
                            </span>
                          </a>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
            <div class="-mr-2 flex md:hidden">
              <button class="text-gray-800 dark:text-white hover:text-gray-300 inline-flex items-center justify-center p-2 rounded-md focus:outline-none">
                <svg
                  width="20"
                  height="20"
                  fill="currentColor"
                  class="h-8 w-8"
                  viewBox="0 0 1792 1792"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path d="M1664 1344v128q0 26-19 45t-45 19h-1408q-26 0-45-19t-19-45v-128q0-26 19-45t45-19h1408q26 0 45 19t19 45zm0-512v128q0 26-19 45t-45 19h-1408q-26 0-45-19t-19-45v-128q0-26 19-45t45-19h1408q26 0 45 19t19 45zm0-512v128q0 26-19 45t-45 19h-1408q-26 0-45-19t-19-45v-128q0-26 19-45t45-19h1408q26 0 45 19t19 45z"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
        <div class="md:hidden">
          <div class="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            <a
              class="text-gray-300 hover:text-gray-800 dark:hover:text-white block px-3 py-2 rounded-md text-base font-medium"
              href="/#"
            >
              Home
            </a>
          </div>
        </div>
      </nav>
      <section className="lg:flex p-4">
        {cards.map((card) => (
          <div class="shadow-lg rounded-2xl w-64 p-4 bg-white relative overflow-hidden m-4">
            <img
              alt="moto"
              src={card.image}
              class="absolute -right-20 -bottom-8 h-full bg-contain w-40 mb-4"
            />
            <div class="w-4/6">
              <p class="text-gray-800 text-lg font-medium mb-2">
                {card.number}
              </p>
              <p class="text-gray-400 text-xs">{card.description}</p>
              <p class="text-indigo-500 text-xl font-medium">
                {microAlgosToString(card.amount)} ALGO
              </p>

              <div class="flex items-center">
                {address !== card.owner ? (
                  <button
                    type="button"
                    onClick={() => buyCard(card)}
                    class="bg-red-500 border-l border-t border-b text-base font-medium rounded-l-md text-white hover:bg-red-600 px-4 py-2"
                  >
                    Buy
                  </button>
                ) : (
                  <button
                    disabled
                    type="button"
                    class="bg-gray-500 border-l border-t border-b text-base font-medium rounded-l-md text-white px-4 py-2"
                  >
                    Buy
                  </button>
                )}
                {address === card.owner && card.bought === 1 && <button
                  type="button"
                  onClick={() => sellCard(card)}
                  class="bg-blue-500 border-t border-b border-r text-base font-medium rounded-r-md text-white hover:bg-blue-600 px-4 py-2"
                >
                  Sell
                </button>}
              </div>
            </div>
          </div>
        ))}
      </section>

      <form onSubmit={formHandler} class="flex w-full space-x-3">
        <div class="w-full max-w-2xl px-5 py-10 m-auto mt-10 bg-white rounded-lg shadow dark:bg-gray-800">
          <div class="mb-6 text-3xl font-light text-center text-gray-800 dark:text-white">
            Create your card !
          </div>
          <div class="grid max-w-xl grid-cols-2 gap-4 m-auto">
            <div class="col-span-2 lg:col-span-1">
              <div class=" relative ">
                <input
                  type="text"
                  id="contact-form-name"
                  class=" rounded-lg border-transparent flex-1 appearance-none border border-gray-300 w-full py-2 px-4 bg-white text-gray-700 placeholder-gray-400 shadow-sm text-base focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                  placeholder="Amount"
                  onChange={(e) => setAmount(e.target.value)}
                />
              </div>
            </div>
            <div class="col-span-2 lg:col-span-1">
              <div class=" relative ">
                <input
                  type="text"
                  id="contact-form-email"
                  class=" rounded-lg border-transparent flex-1 appearance-none border border-gray-300 w-full py-2 px-4 bg-white text-gray-700 placeholder-gray-400 shadow-sm text-base focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                  placeholder="Image"
                  onChange={(e) => setImage(e.target.value)}
                />
              </div>
            </div>
            <div class="col-span-2">
              <label class="text-gray-700" for="name">
                <textarea
                  class="flex-1 appearance-none border border-gray-300 w-full py-2 px-4 bg-white text-gray-700 placeholder-gray-400 rounded-lg text-base focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                  id="comment"
                  placeholder="Description"
                  name="comment"
                  rows="5"
                  cols="40"
                  onChange={(e) => setDescription(e.target.value)}
                ></textarea>
              </label>
            </div>
            <div class="col-span-2 text-right">
              <button
                type="submit"
                class="py-2 px-4  bg-indigo-600 hover:bg-indigo-700 focus:ring-indigo-500 focus:ring-offset-indigo-200 text-white w-full transition ease-in duration-200 text-center text-base font-semibold shadow-md focus:outline-none focus:ring-2 focus:ring-offset-2  rounded-lg "
              >
                Create
              </button>
            </div>
          </div>
        </div>
      </form>
    </div>
  
  );
}

export default App;
