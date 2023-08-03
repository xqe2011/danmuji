const waiters: { [ name: string ]: { doing: boolean, finished: boolean, callbacks: (() => void)[] } } = {};

export function addWaiter(name: string) {
    waiters[name] = { doing: false, finished: false, callbacks: [] };
}

export function listen(name: string) {
    if (!waiters[name]) throw new Error(`No waiter named ${name}!`);
    return new Promise<void>(resolve => {
        if (waiters[name].finished) resolve();
        else waiters[name].callbacks.push(resolve);
    });
}

export function doing(name: string) {
    if (!waiters[name]) throw new Error(`No waiter named ${name}!`);
    if (waiters[name].doing) {
        return false;
    }
    waiters[name].doing = true;
    return true;
}

export function finish(name: string) {
    if (!waiters[name]) throw new Error(`No waiter named ${name}!`);
    waiters[name].finished = true;
    waiters[name].callbacks.forEach(callback => callback());
    waiters[name].callbacks = [];
}