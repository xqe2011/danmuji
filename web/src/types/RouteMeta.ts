import 'vue-router'

export { }

declare module 'vue-router' {
    interface RouteMeta {
        name: string;
        icon: string;
        seo: {
            description: string;
        }
    }
}