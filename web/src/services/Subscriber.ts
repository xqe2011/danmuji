export class Subscriber<T extends Function>
{
    private callbacks: T[] = [];
    private lastCallArguemnts: any = undefined;
    
    constructor(private replay = false) {}

    subscribe(callback: T) {
        if (this.replay && this.lastCallArguemnts !== undefined) {
            callback(...this.lastCallArguemnts);
        }
        this.callbacks.push(callback);
    }

    unsubscribe(callback: T) {
        const index = this.callbacks.indexOf(callback);
        if (index !== -1) {
            this.callbacks.splice(index, 1);
        }
    }

    emit(...args: any[]) {
        this.lastCallArguemnts = args;
        this.callbacks.forEach(callback => callback(...args));
    }
}