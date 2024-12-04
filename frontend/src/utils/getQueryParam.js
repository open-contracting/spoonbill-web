export default (name) => {
    name = name.replace(/[[]/g, '\\[').replace(/[\]]/g, '\\]');
    const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    const results = regex.exec(window.location.hash);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
};
