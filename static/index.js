window.PageOrangepillmerchant = {
  template: '#page-orangepillmerchants',
  delimiters: ['${', '}'],
  data() {
    return {
      wallets: [],
      currencyOptions: ['GBP', 'EUR', 'USD'],
      merchants: [],
      formDialog: {
        show: false,
        data: {
          name: '',
          email: '',
          currency: 'GBP',
          onboarding_amount: null,
          source_wallet_id: null
        }
      },
      merchantsTable: {
        search: '',
        loading: false,
        columns: [
          {name: 'name', align: 'left', label: 'Merchant', field: 'name', sortable: true},
          {name: 'email', align: 'left', label: 'Email', field: 'email', sortable: true},
          {name: 'currency', align: 'left', label: 'Currency', field: 'currency', sortable: true},
          {
            name: 'onboarding_amount',
            align: 'left',
            label: 'Onboarded',
            field: 'onboarding_amount',
            sortable: true
          },
          {
            name: 'repaid_amount',
            align: 'left',
            label: 'Repaid',
            field: 'repaid_amount',
            sortable: true
          },
          {
            name: 'onboarding_completed',
            align: 'left',
            label: 'Complete',
            field: 'onboarding_completed',
            sortable: true
          },
          {name: 'tpos_id', align: 'left', label: 'TPoS', field: 'tpos_id', sortable: true},
          {name: 'updated_at', align: 'left', label: 'Updated', field: 'updated_at', sortable: true}
        ],
        pagination: {
          sortBy: 'updated_at',
          rowsPerPage: 10,
          page: 1,
          descending: true,
          rowsNumber: 0
        }
      }
    }
  },
  watch: {
    'merchantsTable.search': function () {
      this.getMerchants()
    }
  },
  methods: {
    async getWallets() {
      const {data} = await LNbits.api.request('GET', '/orangepillmerchants/api/v1/wallets', null)
      this.wallets = data
      if (!this.formDialog.data.source_wallet_id && this.wallets.length) {
        this.formDialog.data.source_wallet_id = this.wallets[0].id
      }
    },
    showCreateForm() {
      this.formDialog.data = {
        name: '',
        email: '',
        currency: 'GBP',
        onboarding_amount: null,
        source_wallet_id: this.wallets[0]?.id || null
      }
      this.formDialog.show = true
    },
    async saveMerchant() {
      try {
        await LNbits.api.request(
          'POST',
          '/orangepillmerchants/api/v1/merchants',
          null,
          this.formDialog.data
        )
        this.formDialog.show = false
        await this.getMerchants()
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    },
    async getMerchants(props) {
      try {
        this.merchantsTable.loading = true
        const params = LNbits.utils.prepareFilterQuery(this.merchantsTable, props)
        const {data} = await LNbits.api.request(
          'GET',
          `/orangepillmerchants/api/v1/merchants/paginated?${params}`,
          null
        )
        this.merchants = data.data
        this.merchantsTable.pagination.rowsNumber = data.total
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      } finally {
        this.merchantsTable.loading = false
      }
    },
    async resendMerchantEmail(merchant) {
      try {
        await LNbits.api.request(
          'POST',
          `/orangepillmerchants/api/v1/merchants/${merchant.id}/resend`,
          null
        )
        await this.getMerchants()
        Quasar.Notify.create({color: 'positive', message: 'Email resent.'})
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    },
    async deleteMerchant(merchantId) {
      await LNbits.utils.confirmDialog('Delete this onboarding record?').onOk(async () => {
        try {
          await LNbits.api.request(
            'DELETE',
            `/orangepillmerchants/api/v1/merchants/${merchantId}`,
            null
          )
          await this.getMerchants()
        } catch (error) {
          LNbits.utils.notifyApiError(error)
        }
      })
    },
    dateFromNow(date) {
      return moment(date).fromNow()
    },
    tposUrl(row) {
      return `/tpos/${row.tpos_id}`
    }
  },
  async created() {
    await this.getWallets()
    await this.getMerchants()
  }
}
