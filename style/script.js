let buttons = window.parent.document.querySelectorAll('[class=stButton]')
console.log(buttons)

let tabs = window.parent.document.querySelectorAll('[data-baseweb=tab]')
console.log(tabs)

buttons[0].addEventListener('click', function() {tabs[2].click()})
buttons[1].addEventListener('click', function() {tabs[1].click()})
buttons[3].addEventListener('click', function() {tabs[1].click()})
buttons[4].addEventListener('click', function() {tabs[0].click()})
buttons[5].addEventListener('click', function() {tabs[2].click()})
buttons[6].addEventListener('click', function() {tabs[2].click()})
buttons[7].addEventListener('click', function() {tabs[1].click()})
buttons[8].addEventListener('click', function() {tabs[0].click()})
buttons[9].addEventListener('click', function() {tabs[1].click()})