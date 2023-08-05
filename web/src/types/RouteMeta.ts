import 'vue-router'

export { }

declare module 'vue-router' {
    interface RouteMeta {
        name: string;
    }
}