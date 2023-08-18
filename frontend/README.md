# frontend

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npx vue-cli-service serve
```

### Compiles and minifies for production
```
npx vue-cli-service build
```

### Run your unit tests
```
npx vue-cli-service test:unit
```

### Lints and fixes files
```
npx vue-cli-service lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

## gettext

### Extracts all strings from *.vue files
```
npx gettext-extract --removeHTMLWhitespaces --output web-app-ui.pot src/main.js $(find src -type f -name '*.vue')
```

### Compiles *.po files
```
npx gettext-compile --output src/translations/translations.json <filenames>
```
